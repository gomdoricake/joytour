from django.urls import path

from . import views

app_name='guidereports'

urlpatterns = [
    path('', views.index, name='index'),
    path('guidereport_main/', views.guidereport_main, name='guidereport_main'), 
    path('day/guidereport_day/', views.guidereport_day, name='guidereport_day'),
    path('day/guidereport_day_guide_exp', views.guidereport_day_guide_exp, name='guidereport_day_guide_exp'),
    path('inbound/guidereport_inbound_agency/', views.guidereport_inbound_agency, name='guidereport_inbound_agency'),
    path('inbound/guidereport_inbound_events/', views.guidereport_inbound_events, name='guidereport_inbound_events'),
    path('inbound/guidereport_inbound_restaurant_exp/', views.guidereport_inbound_restaurant_exp, name='guidereport_inbound_restaurant_exp'), 
    path('detail/<int:pk>/', views.DetailView, name='detail'),
]