from django.urls import path

from .views import FileUploadView, FileDownloadView, FileExportView, PublicIpView, FileFirstCheckView
from .views import FileSecondCheckView, FileApproveView, FileRejectView, FileApproveListView, FileApproveLogView


urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='upload'),
    path('download/<int:file_id>/', FileDownloadView.as_view(), name='download'),
    path('firstcheck/<int:file_id>/', FileFirstCheckView.as_view(), name='firstcheck'),
    path('secondcheck/<int:file_id>/', FileSecondCheckView.as_view(), name='secondcheck'),
    path('approve/<int:file_id>/', FileApproveView.as_view(), name='approve'),
    path('reject/<int:file_id>/', FileRejectView.as_view(), name='reject'),
    path('approvelist/', FileApproveListView.as_view(), name='approvelist'),
    path('approvelog/', FileApproveLogView.as_view(), name='approvelog'),
    path('export/', FileExportView.as_view(), name='export'),
    path('public_ip/', PublicIpView.as_view(), name='public_ip'),
]
