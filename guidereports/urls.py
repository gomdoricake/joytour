from django.urls import path

from . import views
from .views import main_views, day_views, inbound_views

app_name='guidereports'

urlpatterns = [
    path('guidereport_main/', main_views.guidereport_main, name='guidereport_main'), 
    path('guidereport_confirm/<int:pk>/', main_views.guidereport_confirm, name='guidereport_confirm'),
    path('guidereport_pay/<int:pk>/', main_views.guidereport_pay, name='guidereport_pay'),
    path('guidereport_pdf/<int:pk>/', main_views.guidereport_pdf, name='guidereport_pdf'),
    path('guidereport_confirm_dashboard/<int:pk>/', main_views.guidereport_confirm_dashboard, name='guidereport_confirm_dashboard'),
    path('guidereport_pay_dashboard/<int:pk>/', main_views.guidereport_pay_dashboard, name='guidereport_pay_dashboard'),
    path('guidereport_printed/<int:pk>/', main_views.guidereport_printed, name='guidereport_printed'),

    path('delete_guidereport/<int:pk>/', main_views.delete_guidereport, name='delete_guidereport'),
    path('update_guidereport/<int:pk>/', main_views.update_guidereport, name='update_guidereport'), 
    path('detail/<int:pk>/', main_views.DetailView, name='detail'),

    path('day/guidereport_day/', day_views.guidereport_day, name='guidereport_day'),
    path('day/guidereport_day_guide_exp/', day_views.guidereport_day_guide_exp, name='guidereport_day_guide_exp'),
    path('day/guidereport_day_fuel_exp/', day_views.guidereport_day_fuel_exp, name='guidereport_day_fuel_exp'),
    path('day/guidereport_day_summary/', day_views.guidereport_day_summary, name='guidereport_day_summary'),
    path('day/guidereport_day_fuel_s3_url/', day_views.guidereport_day_fuel_s3_url, name='guidereport_day_fuel_s3_url'),
    path('day/guidereport_day_exp_s3_url/', day_views.guidereport_day_exp_s3_url, name='guidereport_day_exp_s3_url'),
    
    path('inbound/update_attraction/<int:pk>/', inbound_views.update_attraction, name='update_attraction'), 
    path('inbound/update_restaurant/<int:pk>/', inbound_views.update_restaurant, name='update_restaurant'),
    path('inbound/guidereport_inbound_agency/', inbound_views.guidereport_inbound_agency, name='guidereport_inbound_agency'),
    path('inbound/guidereport_inbound_events/', inbound_views.guidereport_inbound_events, name='guidereport_inbound_events'),
    path('inbound/guidereport_inbound_restaurant_exp/', inbound_views.guidereport_inbound_restaurant_exp, name='guidereport_inbound_restaurant_exp'), 
    path('inbound/guidereport_inbound_attraction_exp/', inbound_views.guidereport_inbound_attraction_exp, name='guidereport_inbound_attraction_exp'),
    path('inbound/guidereport_inbound_fuel_exp/', inbound_views.guidereport_inbound_fuel_exp, name='guidereport_inbound_fuel_exp'),
    path('inbound/guidereport_inbound_guide_exp/', inbound_views.guidereport_inbound_guide_exp, name='guidereport_inbound_guide_exp'),
    path('inbound/guidereport_inbound_exp_s3_url/', inbound_views.guidereport_inbound_exp_s3_url, name='guidereport_inbound_exp_s3_url'),
    path('inbound/guidereport_inbound_summary/', inbound_views.guidereport_inbound_summary, name='guidereport_inbound_summary'),
]