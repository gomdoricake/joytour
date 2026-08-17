from django.contrib import admin

from .models import Agent, Group, GroupFile, Itinerary


admin.site.register(Agent)
admin.site.register(Group)
admin.site.register(GroupFile)
admin.site.register(Itinerary)
