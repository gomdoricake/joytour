from django.urls import path

from . import views

app_name='guidereports'

urlpatterns = [
    path('', views.index, name='index'),
    path('guidereport_main/', views.guidereport_main, name='guidereport_main'), 
    path('guidereport_day/', views.guidereport_day, name='guidereport_day'),
    path('guidereport_day_guide_exp', views.guidereport_day_guide_exp, name='guidereport_day_guide_exp'),
    path('guidereport_inbound_agency/', views.guidereport_inbound_agency, name='guidereport_inbound_agency'),
    path('guidereport_inbound_events/', views.guidereport_inbound_events, name='guidereport_inbound_events'), 
    path('detail/<int:pk>/', views.DetailView, name='detail'),
]