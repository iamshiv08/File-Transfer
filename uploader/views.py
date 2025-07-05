# uploader/views.py
import qrcode
import io
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.files.storage import default_storage
from django.conf import settings
from .forms import MultipleFileUploadForm
from .models import UploadedFile
from django.urls import reverse

def home(request):
    if request.method == 'POST':
        form = MultipleFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()
            return redirect('download_page', code=uploaded_file.download_code)
    else:
        form = MultipleFileUploadForm()
    
    return render(request, 'uploader/home.html', {'form': form})

def download_page(request, code):
    uploaded_file = get_object_or_404(UploadedFile, download_code=code)
    files = uploaded_file.files.all()
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    download_url = request.build_absolute_uri(reverse('download_page', args=[code]))
    qr.add_data(download_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert QR code to base64 for embedding in HTML
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_code = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'uploaded_file': uploaded_file,
        'files': files,
        'qr_code': qr_code,
        'download_url': download_url,
        'has_multiple': files.count() > 1,
    }
    
    return render(request, 'uploader/download_page.html', context)

def download_file(request, code, file_id=None):
    uploaded_file = get_object_or_404(UploadedFile, download_code=code)
    
    if file_id:
        # Download single file
        file_item = get_object_or_404(uploaded_file.files, id=file_id)
        file_path = file_item.file.path
        file_name = file_item.original_name
    elif uploaded_file.files.count() > 1 and uploaded_file.zip_file:
        # Download zip file
        file_path = uploaded_file.zip_file.path
        file_name = f"download_{code}.zip"
    else:
        # Fallback to first file
        file_item = uploaded_file.files.first()
        file_path = file_item.file.path
        file_name = file_item.original_name
    
    if not default_storage.exists(file_path):
        raise Http404("File not found")
    
    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/octet-stream")
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response