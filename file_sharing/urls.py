# file_sharing/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from uploader import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('download/<str:code>/', views.download_page, name='download_page'),
    path('download/<str:code>/file/<int:file_id>/', views.download_file, name='download_single_file'),
    path('download/<str:code>/all/', views.download_file, name='download_all_files'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)