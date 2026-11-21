from django.urls import path

from . import views

app_name='guides'

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="guide_detail"),
    path("<int:pk>/payable/", views.guide_payable, name="guide_payable"),
    path("<int:pk>/unpaid/", views.guide_unpaid, name="guide_unpaid"),
    path("<int:pk>/paid/", views.guide_paid, name="guide_paid"), 
    path("<int:pk>/all/", views.guide_all, name="guide_all"),
]