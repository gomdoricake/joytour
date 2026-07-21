from django.urls import path

from . import views

app_name='mypage'

urlpatterns = [
    path("", views.index, name="index"),
    path('login-redirect/', views.login_redirect_view, name='login_redirect'),
    path("update-mypage/<int:pk>/", views.update_mypage, name='update_mypage'),
    path('create-report/', views.create_report, name='create_report'),
    path('unpaid-reports/<int:pk>/', views.unpaid_reports, name='unpaid_reports'),
    path('confirmed-reports/<int:pk>/', views.confirmed_reports, name='confirmed_reports'), 
    path('paid-reports/<int:pk>/', views.paid_reports, name='paid_reports'), 
]