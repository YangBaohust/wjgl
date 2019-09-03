from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser


# 定义用户模型，添加额外的字段
class UserProfile(AbstractUser):
    department = models.CharField(max_length=15, verbose_name='部门', blank=True)
    role = models.CharField(max_length=1, choices=(('2', '监察员'), ('1', '管理员'), ('0', '普通用户')),
                            verbose_name='用户角色', default='0', blank=True)
    is_superuser = models.IntegerField(verbose_name='是否超级管理员', default=0)
    modify_time = models.DateTimeField(default=datetime.now, verbose_name='修改时间')

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


# 定义用户操作日志模型
class UserOperateLog(models.Model):
    username = models.CharField(max_length=20, verbose_name='人员')
    type = models.CharField(max_length=20, verbose_name='操作类型')
    content_id = models.IntegerField(verbose_name='文件编号')
    content = models.CharField(max_length=50, verbose_name='文件名称')
    modify_time = models.DateTimeField(default=datetime.now, verbose_name='操作时间')

    class Meta:
        verbose_name = '用户操作日志'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username + '.' + self.type
