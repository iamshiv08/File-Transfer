# uploader/forms.py
from django import forms
from .models import UploadedFile, FileItem

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class MultipleFileUploadForm(forms.Form):
    files = MultipleFileField(label='Select files')

    def save(self):
        # First create the UploadedFile instance
        uploaded_file = UploadedFile.objects.create()
        
        # Then create FileItem instances with the relationship set
        for file in self.cleaned_data['files']:
            file_item = FileItem.objects.create(
                file=file,
                uploaded_file=uploaded_file,
                original_name=file.name,
                size=file.size
            )
        
        # Create zip if multiple files
        if uploaded_file.files.count() > 1:
            uploaded_file.create_zip()
        
        return uploaded_file