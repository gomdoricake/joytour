from django.shortcuts import render
from django.urls import include, path
from . import views

app_name = 'invoices'

urlpatterns = [
    path('create_or_update_invoice/<int:pk>/', views.create_or_update_invoice, name='create_or_update_invoice'), 
    path('create_mealtype/', views.create_mealtype, name='create_mealtype'),
    path('update_mealtype/<int:pk>/', views.update_mealtype, name='update_mealtype'),
    path('delete_mealtype/<int:pk>/', views.delete_mealtype, name='delete_mealtype'),
    path('create_attractiontype/', views.create_attractiontype, name='create_attractiontype'),
    path('update_attractiontype/<int:pk>/', views.update_attractiontype, name='update_attractiontype'), 
    path('delete_attractiontype/<int:pk>/', views.delete_attractiontype, name='delete_attractiontype'),
    path('update_attractiontype/<int:pk>/', views.update_attractiontype, name='update_attractiontype'),
    path('create_vehicletype/', views.create_vehicletype, name='create_vehicletype'), 
    path('update_vehicletype/<int:pk>/', views.update_vehicletype, name='update_vehicletype'),
    path('delete_vehicletype/<int:pk>/', views.delete_vehicletype, name='delete_vehicletype'),
    path('create_guideinvoicetype/', views.create_guideinvoicetype, name='create_guideinvoicetype'),
    path('update_guideinvoicetype/<int:pk>/', views.update_guideinvoicetype, name='update_guideinvoicetype'),
    path('delete_guideinvoicetype/<int:pk>/', views.delete_guideinvoicetype, name='delete_guideinvoicetype'),
    path('create_guidetiptype/', views.create_guidetiptype, name='create_guidetiptype'),
    path('update_guidetiptype/<int:pk>/', views.update_guidetiptype, name='update_guidetiptype'), 
    path('delete_guidetiptype/<int:pk>/', views.delete_guidetiptype, name='delete_guidetiptype'), 
    path('create_drivertiptype/', views.create_drivertiptype, name='create_drivertiptype'),
    path('update_drivertiptype/<int:pk>/', views.update_drivertiptype, name='update_drivertiptype'),
    path('delete_drivertiptype/<int:pk>/', views.delete_drivertiptype, name='delete_drivertiptype'), 
]
