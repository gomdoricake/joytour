from django.urls import path

from . import views

app_name='guidereports'

urlpatterns = [
    path('', views.index, name='index'),
    path('create_guidereport/', views.create_guidereport, name='create_guidereport')
]