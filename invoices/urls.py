from django.shortcuts import render
from django.urls import include, path
from . import views

app_name = 'invoices'

urlpatterns = [
    path('', views.index, name='index'),
]
