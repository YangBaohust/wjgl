from django.urls import path

from .views import UserLoginView, UserLogoutView
from .views import UserListView, UserAddView, UserDetailView, UserModifyView, UserResetPwd, UserPwdModifyView
from .views import UserOperateView


urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    # 定义用户的相关url
    path('list/', UserListView.as_view(), name='list'),
    path('add/', UserAddView.as_view(), name='add'),
    path('detail/<int:user_id>/', UserDetailView.as_view(), name='detail'),
    path('modify/', UserModifyView.as_view(), name='modify'),
    path('pwdreset/<int:user_id>', UserResetPwd.as_view(), name='pwdreset'),   #  该url为管理员重置用户密码
    path('pwdmodify/', UserPwdModifyView.as_view(), name='pwd_modify'),  #  该url为用户修改自身密码

    # 定义用户操作url
    path('operate_log/', UserOperateView.as_view(), name='operate_log'),
]
