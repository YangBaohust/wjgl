from datetime import datetime

from django.db import models


# 定义文件列表model
class UploadFile(models.Model):
    filename = models.CharField(max_length=200, verbose_name='文件名称')
    filepath = models.CharField(max_length=200, verbose_name='文件路径')
    owner = models.CharField(max_length=200, verbose_name='文件所属用户')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='上传时间')

    class Meta:
        verbose_name = '上传文件列表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.filename


# 定义只有指定的ip才能上传文件
class UploadHost(models.Model):
    host_ip = models.CharField(max_length=300, verbose_name='指定的ip地址')

    class Meta:
        verbose_name = '指定的ip地址'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.host_ip
