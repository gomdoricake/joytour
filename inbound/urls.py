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
    path('group_groupfile/<int:pk>/', views.group_groupfile, name='group_groupfile'),
    path('create_group/', views.create_group, name='create_group'),
    path('update_group/<int:pk>/', views.update_group, name='update_group'), 
    path('delete_group/<int:pk>/', views.delete_group, name='delete_group'),
    path('create_groupfile/<int:pk>/', views.create_groupfile, name='create_groupfile'), 
    path('create_hoteltype/', views.create_hoteltype, name='create_hoteltype'),
    path('update_hoteltype/<int:pk>/', views.update_hoteltype, name='update_hoteltype'),
    path('create_hotel/<int:pk>/', views.create_hotel, name='create_hotel'),
    path('update_hotel/<int:pk>/', views.update_hotel, name='update_hotel'),
    path('create_meeting_board/<int:pk>/', views.create_meeting_board, name='create_meeting_board'),
    path('update_meeting_board/<int:pk>/', views.update_meeting_board, name='update_meeting_board'),
    path('create_flighttype/', views.create_flighttype, name='create_flighttype'), 
]
