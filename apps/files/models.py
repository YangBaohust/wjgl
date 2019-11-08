from datetime import datetime

from django.db import models


# 文件model
class File(models.Model):
    fileno = models.CharField(max_length=18, verbose_name='文件编号')
    filename = models.CharField(max_length=200, verbose_name='文件名称')
    filepath = models.CharField(max_length=200, verbose_name='文件路径')
    owner = models.CharField(max_length=30, verbose_name='文件所属用户')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='上传时间')
    first_check = models.CharField(max_length=1, choices=(('0', '未审批'), ('1', '已审批')), verbose_name='初审', default='0')
    second_check = models.CharField(max_length=1, choices=(('0', '未审批'), ('1', '已审批')), verbose_name='二审', default='0')
    isapprove = models.CharField(max_length=1, choices=(('0', '未审批'), ('1', '已审批'), ('2', '已驳回')), verbose_name='终审', default='0')

    class Meta:
        verbose_name = '文件'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.filename


# 文件审批日志model
class ApproveLog(models.Model):
    fileno = models.CharField(max_length=18, verbose_name='文件编号')
    filename = models.CharField(max_length=200, verbose_name='文件名称')
    owner = models.CharField(max_length=30, verbose_name='文件所属用户')
    add_time = models.DateTimeField(verbose_name='上传时间')
    isapprove = models.CharField(max_length=1, choices=(('1', '已审批'), ('2', '已驳回')), verbose_name='终审')
    approve_time = models.DateTimeField(default=datetime.now, verbose_name='审批时间')

    class Meta:
        verbose_name = '文件审批日志'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.filename


# 公用电脑ip地址model
class PublicIp(models.Model):
    host_ip = models.CharField(max_length=300, verbose_name='公用电脑ip地址', blank=True)

    class Meta:
        verbose_name = '公用电脑ip地址'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.host_ip
