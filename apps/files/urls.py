from django.urls import path

from .views import FileUploadView, FileDownloadView, FileExportView, UploadHostView


urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='upload'),
    path('download/<int:file_id>/', FileDownloadView.as_view(), name='download'),
    path('export/', FileExportView.as_view(), name='export'),
    path('upload_host/', UploadHostView.as_view(), name='upload_host'),
]
