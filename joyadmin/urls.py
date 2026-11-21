from django.urls import path

from . import views

app_name='joyadmin'

urlpatterns = [
    path("", views.index, name="index"),
    path("payable_reports/", views.payable_reports, name='payable_reports'),
    path("paid_reports/", views.paid_reports, name='paid_reports'),
    path("unpaid_reports/", views.unpaid_reports, name='unpaid_reports'), 
    path("all_reports/", views.all_reports, name='all_reports'),
    path('search/', views.search, name='search'),
    path('process_selected_invoices/', views.process_selected_invoices, name='process_selected_invoices'), 
    path('guidefee_rates/', views.guidefee_rates, name='guidefee_rates'),
    path('update_guidefee_rate/<int:pk>/', views.update_guidefee_rate, name='update_guidefee_rate'),
    path('delete_guidefee_rate/<int:pk>/', views.delete_guidefee_rate, name='delete_guidefee_rate'), 
]