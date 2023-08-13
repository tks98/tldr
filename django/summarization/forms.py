from django import forms
from .models import UploadedPDF

class UploadPDFForm(forms.ModelForm):
    class Meta:
        model = UploadedPDF
        fields = ['file']
