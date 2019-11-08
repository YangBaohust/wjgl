from django.contrib import admin
from django.urls import path, include

from files.views import IndexView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('files/', include(('files.urls', 'files'), namespace='files')),
]
