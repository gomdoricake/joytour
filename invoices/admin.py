from django.contrib import admin
from .models import Meal, MealType, Attraction, AttractionType, Vehicle, \
                     VehicleType, GuideInvoice, GuideInvoiceType, \
                     Tip, GuideTipType, DriverTipType,Invoice \


admin.site.register(Invoice)
admin.site.register(Meal)
admin.site.register(MealType)
admin.site.register(Attraction)
admin.site.register(AttractionType)
admin.site.register(Vehicle)
admin.site.register(VehicleType)
admin.site.register(GuideInvoice)
admin.site.register(GuideInvoiceType)
admin.site.register(Tip)
admin.site.register(GuideTipType)
admin.site.register(DriverTipType)