from flask import Flask, render_template, request, redirect, url_for
import openai
import PyPDF2
from io import BytesIO
import os

app = Flask(__name__)

# Retrieve API Key from environment variables to prevent hardcoding secrets
openai.api_key = os.getenv('OPENAI_API_KEY')

def extract_text_from_pdf(pdf_file):
    """
    Extract text content from the given PDF file.

    Args:
        pdf_file: The uploaded PDF file.
    
    Returns:
        Extracted text from the PDF.
    """
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ''.join(page.extract_text() for page in pdf_reader.pages)
    return text

def openai_summarization(text):
    """
    Summarize the provided text using OpenAI.

    Args:
        text: Text to be summarized.
    
    Returns:
        Summarized content.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Provide a concise and coherent summary of the following text: {text}"},
        ],
    )
    return response["choices"][0]["message"]["content"]

@app.route('/', methods=['GET'])
def index():
    """
    Handle GET request and render the file upload page.
    """
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload, extract text from PDF, and summarize it.
    """
    uploaded_file = request.files['file']

    if uploaded_file.filename == '':
        return redirect(url_for('index'))

    text = extract_text_from_pdf(uploaded_file)

    # Handle potential errors during the summarization process
    try:
        summary = openai_summarization(text)
    except Exception as e:
        print(f"Error while summarizing: {e}")
        return "Error occurred during summarization.", 500

    return render_template('summary.html', summary=summary)

if __name__ == '__main__':
    app.run(debug=True)

