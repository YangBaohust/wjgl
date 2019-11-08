from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser


# 定义用户模型，添加额外的字段
class UserProfile(AbstractUser):
    userno = models.CharField(max_length=15, verbose_name='工号')
    department = models.CharField(max_length=15, verbose_name='部门', blank=True)
    role = models.CharField(max_length=1, choices=(('3', '监察稽核员'), ('2', '系统管理员'),
                                                   ('1', '普通员工'), ('0', '离职员工')),
                            verbose_name='用户角色', default='1')
    sub_role = models.CharField(max_length=1, choices=(('2', '二审员'), ('1', '初审员'), ('0', '')),
                                verbose_name='子角色', default='0')
    is_superuser = models.IntegerField(verbose_name='超级管理员', default=0)
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


# 定义用户操作日志模型
class UserOperateLog(models.Model):
    userno = models.CharField(max_length=15, verbose_name='工号')
    username = models.CharField(max_length=20, verbose_name='姓名')
    type = models.CharField(max_length=20, verbose_name='操作类型')
    comment = models.CharField(max_length=20, verbose_name='备注')
    fileno = models.CharField(max_length=18, verbose_name='文件编号')
    filename = models.CharField(max_length=200, verbose_name='文件名称')
    modify_time = models.DateTimeField(default=datetime.now, verbose_name='操作时间')

    class Meta:
        verbose_name = '用户操作日志'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username + '.' + self.type
