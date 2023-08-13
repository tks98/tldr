from django.shortcuts import render, redirect
from .forms import UploadPDFForm
from .models import UploadedPDF
from PyPDF2 import PdfReader
import openai
import os


# Initializing the OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY', "YOUR_DEFAULT_API_KEY")


def view_summary(request):
    """
    Render the summary view of the last uploaded PDF.
    """
    pdf = UploadedPDF.objects.last()  # Get the last uploaded PDF
    if not pdf:
        return redirect('upload_pdf')  # If no PDF found, redirect to the upload page

    context = {
        'pdf': pdf,
    }
    return render(request, 'summarization/summary.html', context)


def upload_pdf(request):
    """
    Handle PDF uploads and summarization.
    """
    if request.method == 'POST':
        form = UploadPDFForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save(commit=False)  # Create instance without saving to the database yet

            # Extract text from PDF using PdfReader
            with open(uploaded_file.file.path, 'rb') as file:
                reader = PdfReader(file)
                text = ''.join(page.extract_text() for page in reader.pages)

            # Summarize with OpenAI
            summarized_text = openai_summarization(text)

            # Set the PDF title as the filename
            uploaded_file.title = os.path.splitext(uploaded_file.file.name)[0]
            uploaded_file.summarized_text = summarized_text  # Store the summarized_text
            uploaded_file.save()  # Save to the database

            return redirect('view_summary')

    else:
        form = UploadPDFForm()

    return render(request, 'summarization/upload.html', {'form': form})


def openai_summarization(text):
    """
    Call the OpenAI API to summarize the provided text.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[ 
            {"role": "user", "content": f"Summarize this: {text}"},
        ],
    )
    return response["choices"][0]["message"]["content"]