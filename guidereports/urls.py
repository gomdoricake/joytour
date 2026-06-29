from django.urls import path

from . import views
from .views import main_views, day_views, inbound_views

app_name='guidereports'

urlpatterns = [
    path('', main_views.index, name='index'),
    path('guidereport_main/', main_views.guidereport_main, name='guidereport_main'), 
    path('guidereport_confirm/<int:pk>/', main_views.guidereport_confirm, name='guidereport_confirm'),
    path('guidereport_pay/<int:pk>/', main_views.guidereport_pay, name='guidereport_pay'),
    path('guidereport_pdf/<int:pk>/', main_views.guidereport_pdf, name='guidereport_pdf'),

    path('delete_guidereport/<int:pk>/', main_views.delete_guidereport, name='delete_guidereport'),
    path('update_guidereport/<int:pk>/', main_views.update_guidereport, name='update_guidereport'), 
    path('detail/<int:pk>/', main_views.DetailView, name='detail'),

    path('day/guidereport_day/', day_views.guidereport_day, name='guidereport_day'),
    path('day/guidereport_day_guide_exp/', day_views.guidereport_day_guide_exp, name='guidereport_day_guide_exp'),
    path('day/guidereport_day_fuel_exp/', day_views.guidereport_day_fuel_exp, name='guidereport_day_fuel_exp'),
    
    path('inbound/guidereport_inbound_agency/', inbound_views.guidereport_inbound_agency, name='guidereport_inbound_agency'),
    path('inbound/guidereport_inbound_events/', inbound_views.guidereport_inbound_events, name='guidereport_inbound_events'),
    path('inbound/guidereport_inbound_restaurant_exp/', inbound_views.guidereport_inbound_restaurant_exp, name='guidereport_inbound_restaurant_exp'), 
    path('inbound/guidereport_inbound_attraction_exp/', inbound_views.guidereport_inbound_attraction_exp, name='guidereport_inbound_attraction_exp'),
    path('inbound/guidereport_inbound_fuel_exp/', inbound_views.guidereport_inbound_fuel_exp, name='guidereport_inbound_fuel_exp'),
    path('inbound/guidereport_inbound_guide_exp/', inbound_views.guidereport_inbound_guide_exp, name='guidereport_inbound_guide_exp'),
]