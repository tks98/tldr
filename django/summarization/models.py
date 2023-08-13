from django.db import models


class UploadedPDF(models.Model):
    file = models.FileField(upload_to='pdfs/')
    summarized_text = models.TextField(null=True, blank=True)
    title = models.CharField(max_length=200, blank=True, null=True)

