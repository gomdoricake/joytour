from django.contrib import admin
from .models import Meal, MealType, Attraction, AttractionType, Vehicle, VehicleType, Invoice

admin.site.register(Invoice)
admin.site.register(Meal)
admin.site.register(MealType)
admin.site.register(Attraction)
admin.site.register(AttractionType)
admin.site.register(Vehicle)
admin.site.register(VehicleType)