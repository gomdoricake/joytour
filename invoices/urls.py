from django.shortcuts import render
from django.urls import include, path
from . import views

from .views import MealTypeListView, AttractionTypeListView, VehicleTypeListView, GuideInvoiceTypeListView

app_name = 'invoices'

urlpatterns = [
    path('<int:pk>/', views.index, name='index'),
    path('create_invoice/<int:pk>/', views.create_invoice, name='create_invoice'), 
    path('mealtype_list/', MealTypeListView.as_view(), name='mealtype_list'),
    path('create_mealtype/', views.create_mealtype, name='create_mealtype'),
    path('attractiontype_list/', AttractionTypeListView.as_view(), name='attractiontype_list'),
    path('create_attractiontype/', views.create_attractiontype, name='create_attractiontype'), 
    path('vehicletype_list/', VehicleTypeListView.as_view(), name='vehicletype_list'),
    path('create_vehicletype/', views.create_vehicletype, name='create_vehicletype'), 
    path('guideinvoicetype_list/', GuideInvoiceTypeListView.as_view(), name='guideinvoicetype_list'), 
    path('create_guideinvoicetype/', views.create_guideinvoicetype, name='create_guideinvoicetype'),
]
