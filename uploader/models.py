# uploader/models.py
import os
import zipfile
import random
import string
from django.db import models
from django.conf import settings

def generate_download_code():
    return ''.join(random.choices(string.digits, k=6))

class UploadedFile(models.Model):
    download_code = models.CharField(max_length=6, default=generate_download_code, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    zip_file = models.FileField(upload_to='zips/', blank=True, null=True)

    def create_zip(self):
        if self.files.count() > 1:
            zip_filename = f"download_{self.download_code}.zip"
            zip_path = os.path.join(settings.MEDIA_ROOT, 'zips', zip_filename)
            
            # Ensure the zips directory exists
            os.makedirs(os.path.dirname(zip_path), exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file_item in self.files.all():
                    zipf.write(file_item.file.path, os.path.basename(file_item.file.path))
            
            self.zip_file.name = os.path.join('zips', zip_filename)
            self.save()

class FileItem(models.Model):
    file = models.FileField(upload_to='uploads/')
    original_name = models.CharField(max_length=255)
    size = models.PositiveIntegerField()
    uploaded_file = models.ForeignKey(UploadedFile, related_name='files', on_delete=models.CASCADE)

    # Removed the custom save method since we're setting fields during creation