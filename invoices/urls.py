from django.shortcuts import render
from django.urls import include, path
from . import views

from .views import MealTypeListView, AttractionTypeListView

app_name = 'invoices'

urlpatterns = [
    path('<int:pk>/', views.index, name='index'),
    path('mealtype_list/', MealTypeListView.as_view(), name='mealtype_list'),
    path('create_mealtype/', views.create_mealtype, name='create_mealtype'),
    path('attractiontype_list/', AttractionTypeListView.as_view(), name='attractiontype_list'),
    path('create_attractiontype/', views.create_attractiontype, name='create_attractiontype'), 
]
