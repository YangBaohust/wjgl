from django.shortcuts import render, redirect, render_to_response
from django.views.generic.base import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db.models import Q
from pure_pagination import Paginator, PageNotAnInteger

from .models import UserProfile, UserOperateLog
from .forms import LoginForm, UserPwdModifyForm, UserInfoForm
from wjgl.settings import per_page
from utils.mixin_utils import LoginRequiredMixin

# 用户初始密码
pwd = '123456'


# 用户的相关视图

# 用戶使用用戶名或工号登陆
class CustomeBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(userno=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


# 用户登录
class UserLoginView(View):
    def get(self, request):
        return render(request, 'users/login.html')

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = request.POST.get('username').strip()
            password = request.POST.get('password').strip()
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                if request.user.role == '0' and request.user.is_superuser != 1:
                    return render(request, 'users/login.html', {'msg': '该账号已锁，请联系管理员'})
                return HttpResponseRedirect(reverse('index'))
            else:
                return render(request, 'users/login.html', {'msg': '账号或密码错误'})
        else:
            return render(request, 'users/login.html', {'msg': '账号或密码错误', 'login_form': login_form})


# 用户退出
class UserLogoutView(View):
    def get(self, request):
        logout(request)
        response = redirect(reverse('users:login'))
        response.delete_cookie('username')
        return response


# 用户修改密码
class UserPwdModifyView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'users/user_pwd_modify.html')

    def post(self, request):
        user_pwd_modify_form = UserPwdModifyForm(request.POST)
        if user_pwd_modify_form.is_valid():
            user = UserProfile.objects.get(username=request.user.username)
            pwd1 = request.POST.get('pwd1').strip()
            pwd2 = request.POST.get('pwd2').strip()
            if pwd1 == pwd2:
                user.password = make_password(pwd1)
                user.save()
                return HttpResponseRedirect((reverse('users:login')))
            else:
                return render(request, 'users/user_pwd_modify.html', {'msg': '两次密码不一致！'})
        else:
            return render(request, 'users/user_pwd_modify.html', {'msg': '密码不能为空！',
                                                                  'user_pwd_modify_form': user_pwd_modify_form})


# 管理员对用户的操作相关视图(管理员可见)
# 用户列表
class UserListView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != '2' and request.user.is_superuser != 1:
            return HttpResponse(status=404)
        search = request.GET.get('search')
        if search:
            search = request.GET.get('search').strip()
            users = UserProfile.objects.filter(Q(userno__icontains=search) | Q(username__icontains=search)
                                               | Q(department__icontains=search), is_superuser=0
                                               ).order_by('-role', 'userno')  # 排除超级管理员
        else:
            users = UserProfile.objects.filter(is_superuser=0).order_by('-role', 'userno')  # 排除超级管理员

        # 分页功能实现
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(users, per_page=per_page, request=request)
        p_contents = p.page(page)
        start = (int(page)-1) * per_page  # 避免分页后每行数据序号从1开始
        return render(request, 'users/user_list.html', {'p_contents': p_contents, 'start': start, 'search': search})


# 用户添加
class UserAddView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != '2' and request.user.is_superuser != 1:
            return HttpResponse(status=404)
        return render(request, 'users/user_add.html')

    def post(self, request):
        userinfo_form = UserInfoForm(request.POST)
        if userinfo_form.is_valid():
            userno = request.POST.get('userno').strip()
            username = request.POST.get('username').strip()
            department = request.POST.get('department').strip()
            role = request.POST.get('role')
            sub_role = request.POST.get('sub_role')
            user = UserProfile.objects.filter(username=username)
            if user:
                return render(request, 'users/user_add.html', {'msg': '用户 '+username+' 已存在！'})
            else:
                new_user = UserProfile(userno=userno, username=username, password=make_password(pwd),
                                       department=department, role=role, sub_role=sub_role)
                new_user.save()
                return HttpResponseRedirect((reverse('users:list')))
        else:
            return render(request, 'users/user_add.html', {'msg': '输入错误！', 'userinfo_form': userinfo_form})


# 用户详情
class UserDetailView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        if request.user.role != '2' and request.user.is_superuser != 1:
            return HttpResponse(status=404)
        user = UserProfile.objects.get(id=user_id)
        return render(request, 'users/user_detail.html', {'user': user})


# 用户修改
class UserModifyView(LoginRequiredMixin, View):
    def post(self, request):
        userinfo_form = UserInfoForm(request.POST)
        user_id = int(request.POST.get('user_id'))
        user = UserProfile.objects.get(id=user_id)
        if userinfo_form.is_valid():
            username = request.POST.get('username').strip()
            other_user = UserProfile.objects.filter(~Q(id=user_id), username=username)
            # 如果修改了用户名，判断是否该用户名与其他用户冲突
            if other_user:
                return render(request, 'users/user_detail.html', {'user': user, 'msg': username+'用户名已存在！'})
            else:
                user.userno = request.POST.get('userno').strip()
                user.username = request.POST.get('username').strip()
                user.department = request.POST.get('department').strip()
                user.role = request.POST.get('role')
                user.sub_role = request.POST.get('sub_role')
                user.save()
                return HttpResponseRedirect((reverse('users:list')))
        else:
            return render(request, 'users/user_detail.html', {'user': user, 'msg': '输入错误！', 'userinfo_form': userinfo_form})


# 重置用户密码
class UserResetPwd(LoginRequiredMixin, View):
    def get(self, request, user_id):
        if request.user.role != '2' and request.user.is_superuser != 1:
            return HttpResponse(status=404)
        user = UserProfile.objects.get(id=user_id)
        user.password = make_password(pwd)
        user.save()
        return HttpResponseRedirect((reverse('users:list')))


# 操作日志
class UserOperateView(LoginRequiredMixin, View):
    def get(self, request):
        search = request.GET.get('search')
        if search:
            search = search.strip()
            if request.user.role == '3' or request.user.is_superuser == 1:
                operate_logs = UserOperateLog.objects.filter(Q(userno__icontains=search) | Q(username__icontains=search)
                                                             | Q(fileno__icontains=search) | Q(filename__icontains=search)
                                                             ).order_by('-modify_time')
            else:
                operate_logs = UserOperateLog.objects.filter(Q(userno__icontains=search) | Q(fileno__icontains=search)
                                                             | Q(filename__icontains=search), username=request.user.username
                                                             ).order_by('-modify_time')
        else:
            if request.user.role == '3' or request.user.is_superuser == 1:
                operate_logs = UserOperateLog.objects.all().order_by('-modify_time')
            else:
                operate_logs = UserOperateLog.objects.filter(username=request.user.username).order_by('-modify_time')

        # 分页功能实现
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(operate_logs, per_page=per_page, request=request)
        p_contents = p.page(page)
        start = (int(page)-1) * per_page  # 避免分页后每行数据序号从1开始

        return render(request, 'users/operate_log.html', {'p_contents': p_contents, 'start': start, 'search': search})


# 定义全局404
def page_not_found(request):
    response = render_to_response('404.html')
    response.status_code = 404
    return response


# 定义全局500
def page_error(request):
    response = render_to_response('500.html')
    response.status_code = 500
    return response
