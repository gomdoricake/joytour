from django.shortcuts import render
from django.urls import include, path
from . import views

from .views import MealTypeListView

app_name = 'invoices'

urlpatterns = [
    path('<int:pk>/', views.index, name='index'),
    path('mealtype_list/', MealTypeListView.as_view(), name='mealtype_list'),
    path('create_mealtype/', views.create_mealtype, name='create_mealtype'),
]
