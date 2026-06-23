from django.urls import path

from . import views

app_name='mypage'

urlpatterns = [
    path("", views.index, name="index"),
    path('login-redirect/', views.login_redirect_view, name='login_redirect'),
    path("update-mypage/<int:pk>/", views.update_mypage, name='update_mypage'),
    path('create-report/', views.create_report, name='create_report'),
    path('review-grade/', views.review_grade, name='review_grade'),
    path('admin/', views.admin, name='admin')
]