from flask import Flask, render_template, request, redirect, url_for, g
import openai
import PyPDF2
import os
import sqlite3
import hashlib

app = Flask(__name__)

DATABASE = 'summaries.db'

# Retrieve API Key from environment variables to prevent hardcoding secrets
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

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

import openai

def openai_summarization(text):
    """
    Summarize the provided text using OpenAI.

    Args:
        text: Text to be summarized.
    
    Returns:
        Summarized content.
    """
    max_tokens = 4000
    truncation_message = "Note: The original text was truncated due to context length limits."
    
    # Truncate text if too long
    if len(text) > max_tokens:
        text = text[:max_tokens] + "..."
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Provide a concise and coherent summary of the following text: {text}"},
        ],
    )
    
    summarized_content = response["choices"][0]["message"]["content"]
    
    if len(text) > max_tokens:
        return summarized_content + " " + truncation_message
    return summarized_content


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
    uploaded_file = request.files.get('file')

    # Check if a file was actually uploaded
    if not uploaded_file:
        return "No file uploaded.", 400

    # Check for empty filename
    if uploaded_file.filename == '':
        return "Invalid file name.", 400

    # Extract text from PDF
    try:
        text = extract_text_from_pdf(uploaded_file)
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return "Error processing the PDF file.", 400

    # Create a hash of the PDF content to use as a unique identifier
    pdf_hash = hashlib.sha256(text.encode()).hexdigest()

    # Check if summary exists in the database
    try:
        cached_summary = query_db('SELECT summary FROM summaries WHERE pdf_hash = ?', [pdf_hash], one=True)
    except Exception as e:
        print(f"Error querying the database: {e}")
        return "Error querying the database.", 500

    if cached_summary:
        return render_template('summary.html', summary=cached_summary[0])

    # Get summary from OpenAI and store in the database
    try:
        summary = openai_summarization(text)
        db = get_db()
        db.execute('INSERT INTO summaries (pdf_hash, summary) VALUES (?, ?)', (pdf_hash, summary))
        db.commit()
    except Exception as e:
        print(f"Error while summarizing or storing in the database: {e}")
        return "Error occurred during summarization.", 500

    return render_template('summary.html', summary=summary)


if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()  # This initializes the database on first run only
    app.run(debug=True)
