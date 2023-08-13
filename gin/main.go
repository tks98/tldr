package main

import (
	"bytes"
	"errors"
	"fmt"
	"github.com/dslipak/pdf"
	"github.com/gin-gonic/gin"
	openai "github.com/sashabaranov/go-openai"
	"golang.org/x/net/context"
	"log"
	"net/http"
	"os"
)

// Constant definitions
const (
	tempDirectory = "temp/"
	templateDir   = "templates/*"
)

var (
	openaiAPIKey = os.Getenv("OPENAI_API_KEY") // Retrieving the API Key from environment variables
)

func main() {
	r := setupRouter()
	err := r.Run(":8080")
	if err != nil {
		return
	}
}

// setupRouter initializes the Gin router and its routes.
func setupRouter() *gin.Engine {
	r := gin.Default()

	r.LoadHTMLGlob(templateDir)
	r.GET("/", showUploadPage)
	r.POST("/upload", handleFileUpload)

	return r
}

// showUploadPage handles the root GET request to render the upload page.
func showUploadPage(c *gin.Context) {
	c.HTML(http.StatusOK, "upload.html", nil)
}

// handleFileUpload processes the uploaded file, extracts and summarizes its content.
func handleFileUpload(c *gin.Context) {
	file, err := c.FormFile("file")
	if err != nil {
		logError("reading file", err)
		c.String(http.StatusBadRequest, "File upload problem")
		return
	}

	// Save the file to a temporary location
	tempPath := tempDirectory + file.Filename
	defer os.Remove(tempPath) // ensure temp file gets removed even if there's an error

	if err = c.SaveUploadedFile(file, tempPath); err != nil {
		logError("saving file", err)
		c.String(http.StatusInternalServerError, "Failed to save uploaded file")
		return
	}

	text, err := extractTextFromPDF(tempPath)
	if err != nil {
		logError("extracting text from PDF", err)
		c.String(http.StatusInternalServerError, fmt.Sprintf("Failed: %s", err.Error()))
		return
	}

	summary, err := openaiSummarization(text)
	if err != nil {
		logError("summarizing text", err)
		c.String(http.StatusInternalServerError, "Failed to summarize text")
		return
	}

	c.HTML(http.StatusOK, "summary.html", gin.H{"summary": summary})
}

// extractTextFromPDF processes the provided file path to extract text content from a PDF.
func extractTextFromPDF(filePath string) (string, error) {
	f, err := pdf.Open(filePath)
	if err != nil {
		return "", errors.New("failed to process PDF")
	}

	var buf bytes.Buffer
	b, err := f.GetPlainText()
	if err != nil {
		return "", errors.New("failed to extract text from PDF")
	}

	_, err = buf.ReadFrom(b)
	if err != nil {
		return "", err
	}

	return buf.String(), nil
}

// openaiSummarization uses OpenAI to generate a summary of the provided text.
func openaiSummarization(text string) (string, error) {
	client := openai.NewClient(openaiAPIKey)
	resp, err := client.CreateChatCompletion(
		context.Background(),
		openai.ChatCompletionRequest{
			Model: openai.GPT3Dot5Turbo,
			Messages: []openai.ChatCompletionMessage{
				{
					Role:    openai.ChatMessageRoleUser,
					Content: "Provide a concise and coherent summary of the following text: " + text,
				},
			},
		},
	)

	if err != nil {
		return "", err
	}

	return resp.Choices[0].Message.Content, nil
}

// logError is a utility function to format and log errors.
func logError(action string, err error) {
	log.Printf("Error %s: %v", action, err)
}
