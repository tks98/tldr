package main

import (
	"bytes"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"io"
	"io/ioutil"
	"mime/multipart"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
)

// Setup the test environment
func setupRouterForTesting() *gin.Engine {
	gin.SetMode(gin.TestMode)
	r := setupRouter()
	return r
}

func createMultipartRequest(url, fieldName, fileName string) (*http.Request, error) {
	file, err := os.Open(fileName)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)
	part, err := writer.CreateFormFile(fieldName, file.Name())
	if err != nil {
		return nil, err
	}
	_, err = io.Copy(part, file)

	err = writer.Close()
	if err != nil {
		return nil, err
	}

	request, err := http.NewRequest("POST", url, body)
	request.Header.Set("Content-Type", writer.FormDataContentType())
	return request, err
}

// Test PDF Upload functionality
func TestPDFUpload(t *testing.T) {
	r := setupRouterForTesting()

	// Test valid PDF upload
	request, err := createMultipartRequest("/upload", "file", "test_data/sample.pdf")
	if err != nil {
		t.Fatal(err)
	}
	response := httptest.NewRecorder()

	r.ServeHTTP(response, request)
	assert.Equal(t, http.StatusOK, response.Code)

	// Test invalid file type
	request, err = createMultipartRequest("/upload", "file", "test_data/sample.txt")
	if err != nil {
		t.Fatal(err)
	}
	response = httptest.NewRecorder()

	r.ServeHTTP(response, request)
	assert.NotEqual(t, http.StatusOK, response.Code)
}

// Test Summary Generation
func TestSummaryGeneration(t *testing.T) {
	r := setupRouterForTesting()

	request, err := createMultipartRequest("/upload", "file", "test_data/sample.pdf")
	if err != nil {
		t.Fatal(err)
	}
	response := httptest.NewRecorder()

	r.ServeHTTP(response, request)
	assert.Equal(t, http.StatusOK, response.Code)

	body, _ := ioutil.ReadAll(response.Body)
	assert.Contains(t, string(body), "summary") // Check if the summary is present in the response
}

// Test Exception Handling
func TestExceptionHandling(t *testing.T) {
	r := setupRouterForTesting()

	// Empty file
	emptyFile := bytes.NewBuffer(nil)
	request, _ := http.NewRequest(http.MethodPost, "/upload", emptyFile)
	request.Header.Add("Content-Type", "multipart/form-data")
	response := httptest.NewRecorder()

	r.ServeHTTP(response, request)
	assert.NotEqual(t, http.StatusOK, response.Code)
}

// Test Database Cache
func TestDatabaseCache(t *testing.T) {
	r := setupRouterForTesting()

	// First request
	request, err := createMultipartRequest("/upload", "file", "test_data/sample.pdf")
	if err != nil {
		t.Fatal(err)
	}
	response := httptest.NewRecorder()

	r.ServeHTTP(response, request)
	assert.Equal(t, http.StatusOK, response.Code)

	// Second request
	request, err = createMultipartRequest("/upload", "file", "test_data/sample.pdf")
	if err != nil {
		t.Fatal(err)
	}
	response = httptest.NewRecorder()

	r.ServeHTTP(response, request)
	assert.Equal(t, http.StatusOK, response.Code)
}

func TestMain(m *testing.M) {
	// Setup and teardown for tests can go here
	os.Exit(m.Run())
}
