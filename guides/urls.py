from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:guide_id>/", views.guide_detail, name="guide_detail"),
]