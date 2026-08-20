from django.contrib import admin
from django.urls import include, path
from . import views

app_name = 'inbound'

urlpatterns = [
    path('', views.index, name='index'),
    path('tariff/', views.tariff, name='tariff'),
    path('agent_list/', views.agent_list, name='agent_list'),
    path('agent_detail/<int:pk>/', views.agent_detail, name='agent_detail'), 
    path('create_agent/', views.create_agent, name='create_agent'),
    path('update_agent/<int:pk>/', views.update_agent, name='update_agent'),
    path('delete_agent/<int:pk>/', views.delete_agent, name='delete_agent'), 
    path('group_list/', views.group_list, name='group_list'), 
    path('group_detail/<int:pk>/', views.group_detail, name='group_detail'),
    path('create_group/', views.create_group, name='create_group'),
    path('update_group/<int:pk>/', views.update_group, name='update_group'), 
    path('delete_group/<int:pk>/', views.delete_group, name='delete_group'),
    path('create_groupfile/<int:pk>/', views.create_groupfile, name='create_groupfile'), 
]
