from django.urls import path

from . import views

app_name='guides'

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:guide_id>/", views.guide_detail, name="guide_detail"),
    path("create/", views.create_guide, name="create_guide"),
]