from django.urls import path

from . import views

app_name='mypage'

urlpatterns = [
    path("", views.mypage, name="mypage"),
    path('login-redirect/', views.login_redirect_view, name='login_redirect'),
    path('admin/', views.admin, name='admin')
]