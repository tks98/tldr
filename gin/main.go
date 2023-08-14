package main

import (
	"bytes"
	"crypto/sha256"
	"database/sql"
	"errors"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/dslipak/pdf"
	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	openai "github.com/sashabaranov/go-openai"
	"golang.org/x/net/context"
)

const (
	tempDirectory = "temp/"
	templateDir   = "templates/*"
)

var (
	openaiAPIKey = os.Getenv("OPENAI_API_KEY") // OpenAI API key
	db           *sql.DB                       // Database instance
)

func main() {
	r := setupRouter()
	defer db.Close() // Close the database connection upon exit
	r.Run(":8080")
}

// Initialize and set up SQLite database
func init() {
	var err error
	db, err = sql.Open("sqlite3", "./summaries.db")
	if err != nil {
		log.Fatal(err)
	}

	// Create table if not already present
	_, err = db.Exec(`
        CREATE TABLE IF NOT EXISTS summaries (
            pdf_hash TEXT PRIMARY KEY,
            summary TEXT
        )
    `)
	if err != nil {
		log.Fatal(err)
	}
}

// Retrieve summary from database using the PDF hash
func getSummaryFromDB(pdfHash string) (string, error) {
	var summary string
	err := db.QueryRow("SELECT summary FROM summaries WHERE pdf_hash = ?", pdfHash).Scan(&summary)
	return summary, err
}

// Save the summary to the database
func saveSummaryToDB(pdfHash, summary string) error {
	_, err := db.Exec("INSERT INTO summaries (pdf_hash, summary) VALUES (?, ?)", pdfHash, summary)
	return err
}

// Generate hash for content (used for caching mechanism)
func hashContent(content string) string {
	return fmt.Sprintf("%x", sha256.Sum256([]byte(content)))
}

// Set up Gin routes and middleware
func setupRouter() *gin.Engine {
	r := gin.Default()
	r.LoadHTMLGlob(templateDir)
	r.GET("/", showUploadPage)
	r.POST("/upload", handleFileUpload)
	return r
}

// Show the file upload page
func showUploadPage(c *gin.Context) {
	c.HTML(http.StatusOK, "upload.html", nil)
}

// Handle file upload, extraction, and summarization
func handleFileUpload(c *gin.Context) {
	file, err := c.FormFile("file")
	if err != nil {
		logError("reading file", err)
		c.String(http.StatusBadRequest, "File upload problem")
		return
	}

	// Save the file temporarily
	tempPath := tempDirectory + file.Filename
	defer os.Remove(tempPath)

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

	pdfHash := hashContent(text)

	// Check cache before generating a new summary
	cachedSummary, err := getSummaryFromDB(pdfHash)
	if err == nil && cachedSummary != "" {
		c.HTML(http.StatusOK, "summary.html", gin.H{"summary": cachedSummary})
		return
	}

	summary, err := openaiSummarization(text)
	if err != nil {
		logError("summarizing text", err)
		c.String(http.StatusInternalServerError, "Failed to summarize text")
		return
	}

	// Cache the generated summary
	if err := saveSummaryToDB(pdfHash, summary); err != nil {
		logError("saving summary to database", err)
	}

	c.HTML(http.StatusOK, "summary.html", gin.H{"summary": summary})
}

// Extract text content from PDF
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

// Summarize the text content using OpenAI
func openaiSummarization(text string) (string, error) {
	const maxTokens = 4000
	const truncationMessage = "Note: The original text was truncated due to context length limits."

	client := openai.NewClient(openaiAPIKey)

	// Truncate text if too long
	if len(text) > maxTokens {
		text = text[:maxTokens] + "..."
	}

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

	if len(text) > maxTokens {
		return resp.Choices[0].Message.Content + " " + truncationMessage, nil
	}
	return resp.Choices[0].Message.Content, nil
}

// Log errors with a specified action context
func logError(action string, err error) {
	log.Printf("Error %s: %v", action, err)
}
