from django.urls import path

from . import views

app_name='guidereports'

urlpatterns = [
    path('', views.index, name='index'),
    path('guidereport_step1/', views.guidereport_step1, name='guidereport_step1'), 
    path('<int:pk>/guidereport_step2/', views.guidereport_step2, name='guidereport_step2'),
    path('detail/<int:pk>/', views.DetailView, name='detail'),
]