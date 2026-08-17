from django.shortcuts import render
from django.urls import include, path
from . import views

app_name = 'invoices'

urlpatterns = [
    path('create_or_update_invoice/<int:pk>/', views.create_or_update_invoice, name='create_or_update_invoice'), 
    path('mealtype_list/', views.mealtype_list, name='mealtype_list'),
    path('create_mealtype/', views.create_mealtype, name='create_mealtype'),
    path('update_mealtype/<int:pk>/', views.update_mealtype, name='update_mealtype'),
    path('attractiontype_list/', views.attractiontype_list, name='attractiontype_list'),
    path('create_attractiontype/', views.create_attractiontype, name='create_attractiontype'),
    path('update_attractiontype/<int:pk>/', views.update_attractiontype, name='update_attractiontype'), 
    path('update_attractiontype/<int:pk>/', views.update_attractiontype, name='update_attractiontype'),
    path('vehicletype_list/', views.vehicletype_list, name='vehicletype_list'),
    path('create_vehicletype/', views.create_vehicletype, name='create_vehicletype'), 
    path('update_vehicletype/<int:pk>/', views.update_vehicletype, name='update_vehicletype'),
    path('guideinvoicetype_list/', views.guideinvoicetype_list, name='guideinvoicetype_list'), 
    path('create_guideinvoicetype/', views.create_guideinvoicetype, name='create_guideinvoicetype'),
    path('update_guideinvoicetype/<int:pk>/', views.update_guideinvoicetype, name='update_guideinvoicetype'),
    path('tiptype_list/', views.tiptype_list, name='tiptype_list'), 
    path('create_guidetiptype/', views.create_guidetiptype, name='create_guidetiptype'),
    path('update_guidetiptype/<int:pk>/', views.update_guidetiptype, name='update_guidetiptype'), 
    path('create_drivertiptype/', views.create_drivertiptype, name='create_drivertiptype'),
    path('update_drivertiptype/<int:pk>/', views.update_drivertiptype, name='update_drivertiptype')
]
