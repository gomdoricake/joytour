from django.contrib import admin
from .models import GuideReport, GuideExp, Event, RestaurantExp, AttractionExp

admin.site.register(GuideReport)
admin.site.register(Event)
admin.site.register(GuideExp)
admin.site.register(RestaurantExp)
admin.site.register(AttractionExp)