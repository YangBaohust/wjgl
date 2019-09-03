from django.contrib import admin

from .models import UploadFile


class UploadFileAdmin(admin.ModelAdmin):
    pass


admin.site.register(UploadFile, UploadFileAdmin)
