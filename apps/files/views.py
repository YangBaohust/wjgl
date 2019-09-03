import csv
import os
import datetime

from django.shortcuts import render
from django.views.generic.base import View
from django.http.response import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.http import FileResponse
from django.utils.http import urlquote
from django.db.models import Q
from pure_pagination import Paginator, PageNotAnInteger

from .models import UploadFile, UploadHost
from users.models import UserOperateLog
from wjgl.settings import per_page, root_path
from utils.mixin_utils import LoginRequiredMixin


# 文件列表
class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        search = request.GET.get('search')
        if search:
            search = request.GET.get('search').strip()
            if request.user.role == '2' or request.user.is_superuser == 1:
                files = UploadFile.objects.filter(Q(filename__icontains=search) | Q(owner__icontains=search)).order_by(
                    '-add_time')
            else:
                files = UploadFile.objects.filter(filename__icontains=search, owner=request.user.username).order_by(
                    '-add_time')
        else:
            if request.user.role == '2' or request.user.is_superuser == 1:
                files = UploadFile.objects.all().order_by('-add_time')
            else:
                files = UploadFile.objects.filter(owner=request.user.username).order_by('-add_time')

        # 分页功能实现
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(files, per_page=per_page, request=request)
        p_files = p.page(page)
        start = (int(page)-1) * per_page  # 避免分页后每行数据序号从1开始
        return render(request, 'files/index.html', {'p_files': p_files, 'start': start, 'search': search})


# 获取用户的ip地址
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# 文件上传
class FileUploadView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'files/file_upload.html', {})

    def post(self, request):
        ip = get_client_ip(request)
        if UploadHost.objects.first():
            allowed_ip = UploadHost.objects.first().host_ip
        else:
            allowed_ip = ''
        if ip not in allowed_ip:
            return render(request, 'files/file_upload.html', {'msg': '请在指定电脑上传文件'})
        my_file = request.FILES.get('myfile', None)
        if not my_file:
            return render(request, 'files/file_upload.html', {'msg': '没有选择文件'})
        if my_file.name[-4:].lower() in('.exe', '.bat'):
            return render(request, 'files/file_upload.html', {'msg': '请勿上传.exe和.bat文件'})
        year = str(datetime.datetime.now().year)
        month = str(datetime.datetime.now().month)
        day = str(datetime.datetime.now().day)
        username = request.user.username.upper()
        upload_path = os.path.join(root_path, username, year, month, day)
        if os.path.isfile(os.path.join(upload_path, my_file.name)):
            return render(request, 'files/file_upload.html', {'msg': my_file.name + '已存在'})
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
        with open(os.path.join(upload_path, my_file.name), 'wb+') as f:
            for chunk in my_file.chunks():
                f.write(chunk)

        # 将上传记录插入到文件表中
        records = UploadFile()
        records.filename = my_file.name
        records.filepath = upload_path
        records.owner = username
        records.save()

        # 将上传记录插入到日志记录中
        logs = UserOperateLog()
        logs.username = username
        logs.type = '上传'
        logs.content = my_file.name
        logs.content_id = records.id
        logs.save()
        return HttpResponseRedirect((reverse('index')))


# 文件下载
class FileDownloadView(LoginRequiredMixin, View):
    def get(self, request, file_id):
        download_file = UploadFile.objects.get(id=file_id)
        if (request.user.username.upper() != download_file.owner.upper()
                and request.user.role != '2'
                and request.user.is_superuser != 1):
            return HttpResponse(status=404)
        file_name = download_file.filename
        file_path = download_file.filepath
        if not os.path.isfile(os.path.join(file_path, file_name)):
            return render(request, 'files/file_download_error.html', {})
        file = open(os.path.join(file_path, file_name), 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment; filename=' + urlquote(file_name)

        # 将下载记录插入到日志记录中
        logs = UserOperateLog()
        logs.username = request.user.username.upper()
        logs.type = '下载'
        logs.content = file_name
        logs.content_id = file_id
        logs.save()
        return response


# 文件列表导出
class FileExportView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != '2' and request.user.is_superuser != 1:
            return HttpResponse(status=404)
        search = request.GET.get('search')
        if search:
            search = request.GET.get('search').strip()
            files = UploadFile.objects.filter(Q(filename__icontains=search) | Q(owner__icontains=search)).order_by(
                '-add_time')
        else:
            files = UploadFile.objects.all().order_by('-add_time')

        files = files.values('id', 'filename', 'filepath', 'owner', 'add_time')
        colnames = ['文件编号', '文件名', '文件路径', '上传用户', '上传时间']
        response = create_excel(colnames, files, 'wjgl')
        return response


def create_excel(columns, content, file_name):
    """创建导出csv的函数"""
    file_name = file_name + '.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + file_name
    response.charset = 'gbk'
    writer = csv.writer(response)
    writer.writerow(columns)
    for i in content:
        writer.writerow([i['id'], i['filename'], i['filepath'], i['owner'], i['add_time'].strftime(
            '%Y/%m/%d %H:%M:%S')])
    return response


# 只有指定的ip才能上传
class UploadHostView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != '1' and request.user.is_superuser != 1:
            return HttpResponse(status=404)
        upload_host = UploadHost.objects.first()
        return render(request, 'files/settings.html', {'upload_host': upload_host})

    def post(self, request):
        upload_host = UploadHost.objects.first()
        if not upload_host:
            upload_host = UploadHost()
        upload_host.host_ip = request.POST.get('upload_host')
        upload_host.save()
        return HttpResponseRedirect((reverse('index')))