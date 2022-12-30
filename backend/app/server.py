from flask import Flask, request
from io import BytesIO
from PyPDF2 import PdfFileReader
from flask_cors import CORS, cross_origin
from summary import summarize
from waitress import serve
import logging

app = Flask(__name__)
CORS(app)
logger = logging.getLogger("waitress")
logger.setLevel(logging.INFO)


@app.route('/', methods=['GET'])
@cross_origin()
def health():
    return '', 200

@app.route('/summarize', methods=['POST'])
@cross_origin()
def pdf_parser():
    logger.info("Recieved pdf parse request")
    # Get the PDF file from the request
    pdf_file = request.files['pdf']

    # Open the PDF file using PyPDF2
    pdf_reader = PdfFileReader(BytesIO(pdf_file.read()))

    # Extract the text from the PDF
    text = ''
    for page_num in range(pdf_reader.getNumPages()):
        text += pdf_reader.getPage(page_num).extractText()

    # Return the text as the response
    return summarize(text[0:5000])

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=5001)