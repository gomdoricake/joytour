from django.contrib import admin
from .models import Meal, MealType, Invoice

admin.site.register(Meal)
admin.site.register(MealType)
admin.site.register(Invoice)