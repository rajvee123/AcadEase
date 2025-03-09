from django import forms
from .models import UploadedFile

class FileUploadForm(forms.ModelForm):
    file = forms.FileField()

    class Meta:
        model = UploadedFile
        fields = ['category', 'file']
