from django.shortcuts import render
from django.urls import include, path
from . import views

from .views import AttractionTypeListView, VehicleTypeListView, GuideInvoiceTypeListView

app_name = 'invoices'

urlpatterns = [
    path('create_or_update_invoice/<int:pk>/', views.create_or_update_invoice, name='create_or_update_invoice'), 
    path('mealtype_list/', views.mealtype_list, name='mealtype_list'),
    path('create_mealtype/', views.create_mealtype, name='create_mealtype'),
    path('update_mealtype/<int:pk>/', views.update_mealtype, name='update_mealtype'),
    path('attractiontype_list/', AttractionTypeListView.as_view(), name='attractiontype_list'),
    path('create_attractiontype/', views.create_attractiontype, name='create_attractiontype'), 
    path('vehicletype_list/', VehicleTypeListView.as_view(), name='vehicletype_list'),
    path('create_vehicletype/', views.create_vehicletype, name='create_vehicletype'), 
    path('guideinvoicetype_list/', GuideInvoiceTypeListView.as_view(), name='guideinvoicetype_list'), 
    path('create_guideinvoicetype/', views.create_guideinvoicetype, name='create_guideinvoicetype'),
    path('tiptype_list/', views.tiptype_list, name='tiptype_list'), 
    path('create_guidetiptype/', views.create_guidetiptype, name='create_guidetiptype'),
    path('create_drivertiptype/', views.create_drivertiptype, name='create_drivertiptype'),
]
