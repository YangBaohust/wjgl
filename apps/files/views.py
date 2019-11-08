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

from .models import File, PublicIp, ApproveLog
from users.models import UserOperateLog
from wjgl.settings import per_page, root_path
from utils.mixin_utils import LoginRequiredMixin


# 首页(文件列表)
class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        search = request.GET.get('search')
        if search:
            search = search.strip()
            if request.user.role == '3' or request.user.is_superuser == 1:
                files = File.objects.filter(Q(fileno__icontains=search) | Q(filename__icontains=search)
                                            | Q(owner__icontains=search)).order_by('-add_time')
            else:
                files = File.objects.filter(Q(fileno__icontains=search) | Q(filename__icontains=search),
                                            owner=request.user.username).order_by( '-add_time')
        else:
            if request.user.role == '3' or request.user.is_superuser == 1:
                files = File.objects.all().order_by('-add_time')
            else:
                files = File.objects.filter(owner=request.user.username).order_by('-add_time')

        # 分页功能实现
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(files, per_page=per_page, request=request)
        p_contents = p.page(page)
        start = (int(page)-1) * per_page  # 避免分页后每行数据序号从1开始

        return render(request, 'files/index.html', {'p_contents': p_contents, 'start': start, 'search': search})


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
        my_file = request.FILES.get('myfile', None)
        if not my_file:
            return render(request, 'files/file_upload.html', {'msg': '没有选择文件'})
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
        records = File()
        records.fileno = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'))[:17]  # 时间精确到0.001s，用作文件的编号
        records.filename = my_file.name
        records.filepath = upload_path
        records.owner = username
        records.save()

        # 将上传记录插入到日志记录中
        logs = UserOperateLog()
        logs.userno = request.user.userno
        logs.username = username
        logs.type = '上传'
        logs.fileno = records.fileno
        logs.filename = records.filename

        # 判断上传文件是否通过公用电脑上传
        ip = get_client_ip(request)
        public_ip = PublicIp.objects.first()
        if public_ip:
            if ip in public_ip.host_ip:
                logs.comment = '拷入'
            else:
                logs.comment = ''

        logs.save()

        return HttpResponseRedirect((reverse('index')))


# 文件一审
class FileFirstCheckView(LoginRequiredMixin, View):
    def get(self, request, file_id):
        if request.user.role != '3' or request.user.sub_role != '1':
            return HttpResponse(status=404)
        file = File.objects.get(id=file_id)
        if file.first_check == '0':
            file.first_check = '1'
        else:
            file.first_check = '0'
        file.save()
        return HttpResponseRedirect((reverse('index')))


# 文件二审
class FileSecondCheckView(LoginRequiredMixin, View):
    def get(self, request, file_id):
        if request.user.role != '3' or request.user.sub_role != '2':
            return HttpResponse(status=404)
        file = File.objects.get(id=file_id)
        if file.second_check == '0':
            file.second_check = '1'
        else:
            file.second_check = '0'
        file.save()
        return HttpResponseRedirect((reverse('index')))


# 文件终审待审列表
class FileApproveListView(LoginRequiredMixin, View):
    def get(self, request):
        search = request.GET.get('search')
        if search:
            search = search.strip()
            files = File.objects.filter(~Q(owner=request.user.username), Q(fileno__icontains=search)
                                        | Q(filename__icontains=search) | Q(owner__icontains=search),
                                        first_check='1', second_check='1', isapprove='0').order_by('-add_time')
        else:
            files = File.objects.filter(~Q(owner=request.user.username), first_check='1', second_check='1',
                                        isapprove='0').order_by('-add_time')

        # 分页功能实现
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(files, per_page=per_page, request=request)
        p_contents = p.page(page)
        start = (int(page)-1) * per_page  # 避免分页后每行数据序号从1开始
        return render(request, 'files/file_approve_list.html', {'p_contents': p_contents, 'start': start, 'search': search})


# 文件终审
class FileApproveView(LoginRequiredMixin, View):
    def get(self, request, file_id):
        file = File.objects.get(id=file_id)
        if request.user.username == file.owner:
            return HttpResponse(status=404)
        if file.isapprove == '0':
            file.isapprove = '1'
        else:
            file.isapprove = '0'
        file.save()

        # 插入审批日志
        logs = ApproveLog()
        logs.fileno = file.fileno
        logs.filename = file.filename
        logs.owner = file.owner
        logs.add_time = file.add_time
        logs.isapprove = file.isapprove
        logs.save()

        return HttpResponseRedirect((reverse('files:approvelist')))


# 文件终审退回
class FileRejectView(LoginRequiredMixin, View):
    def get(self, request, file_id):
        file = File.objects.get(id=file_id)
        if request.user.username == file.owner:
            return HttpResponse(status=404)
        file.isapprove = '2'
        file.save()

        # 插入审批日志
        logs = ApproveLog()
        logs.fileno = file.fileno
        logs.filename = file.filename
        logs.owner = file.owner
        logs.add_time = file.add_time
        logs.isapprove = file.isapprove
        logs.save()

        return HttpResponseRedirect((reverse('files:approvelist')))


# 文件审批记录
class FileApproveLogView(LoginRequiredMixin, View):
    def get(self, request):
        search = request.GET.get('search')
        if search:
            search = search.strip()
            logs = ApproveLog.objects.filter(Q(fileno__icontains=search) | Q(filename__icontains=search)
                                             | Q(owner__icontains=search)).order_by('-approve_time')
        else:
            logs = ApproveLog.objects.all() .order_by('-approve_time')

        # 分页功能实现
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(logs, per_page=per_page, request=request)
        p_contents = p.page(page)
        start = (int(page)-1) * per_page  # 避免分页后每行数据序号从1开始
        return render(request, 'files/file_approve_log.html', {'p_contents': p_contents, 'start': start, 'search': search})


# 文件下载
class FileDownloadView(LoginRequiredMixin, View):
    def get(self, request, file_id):
        file = File.objects.get(id=file_id)
        if (request.user.username.upper() != file.owner.upper() and request.user.role != '3' and request.user.is_superuser != 1):
            return HttpResponse(status=404)

        # 通过flag判断各种情况
        flag = ''

        ip = get_client_ip(request)
        public_ip = PublicIp.objects.first()
        if public_ip:
            if ip in public_ip.host_ip:
                if file.first_check == '1' and file.second_check == '1' and file.isapprove == '1':
                    flag = '公用可下载'
                else:
                    flag = '公用不可下载'
        else:
            flag = '普通下载'

        if flag == '公用不可下载':
            return render(request, 'files/file_download_error.html', {'msg': '该公用电脑无法下载，请联系管理员~'})
        else:
            filename = file.filename
            filepath = file.filepath
            if not os.path.isfile(os.path.join(filepath, filename)):
                return render(request, 'files/file_download_error.html', {'msg': '文件可能已经被删除，请联系管理员~'})
            download_file = open(os.path.join(filepath, filename), 'rb')
            response = FileResponse(download_file)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment; filename=' + urlquote(filename)

            # 将下载记录插入到日志记录中
            logs = UserOperateLog()
            logs.userno = request.user.userno
            logs.username = request.user.username.upper()
            logs.type = '下载'
            logs.filename = filename
            logs.fileno = file.fileno
            if flag == '公用可下载':
                logs.comment = '拷出'
            else:
                logs.comment = ''
            logs.save()

            return response


# 文件列表导出
class FileExportView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != '3' and request.user.is_superuser != 1:
            return HttpResponse(status=404)
        search = request.GET.get('search')
        if search:
            search = request.GET.get('search').strip()
            files = File.objects.filter(Q(fileno__icontains=search) | Q(filename__icontains=search)
                                        | Q(owner__icontains=search)).order_by('-add_time')
        else:
            files = File.objects.all().order_by('-add_time')

        files = files.values('fileno', 'filename', 'filepath', 'owner', 'add_time')
        colnames = ['文件编号', '文件名', '文件路径', '上传用户', '上传时间']
        response = create_excel(colnames, files, 'wjgl')
        return response


def create_excel(columns, content, filename):
    """创建导出csv的函数"""
    filename = filename + '.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    response.charset = 'gbk'
    writer = csv.writer(response)
    writer.writerow(columns)
    for i in content:
        writer.writerow([i['fileno'], i['filename'], i['filepath'], i['owner'], i['add_time'].strftime( '%Y/%m/%d %H:%M:%S')])
    return response


# 公用电脑ip
class PublicIpView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != '2' and request.user.is_superuser != 1:
            return HttpResponse(status=404)
        public_ip = PublicIp.objects.first()
        return render(request, 'files/public_ip.html', {'public_ip': public_ip})

    def post(self, request):
        public_ip = PublicIp.objects.first()
        if not public_ip:
            public_ip = PublicIp()
        public_ip.host_ip = request.POST.get('host_ip')
        public_ip.save()
        return HttpResponseRedirect((reverse('index')))
