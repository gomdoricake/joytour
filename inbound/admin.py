from django.contrib import admin

from .models import Agent, Group, GroupFile, Itinerary, Hotel, HotelType, Flight, FlightType,ItineraryDate


admin.site.register(Agent)
admin.site.register(Group)
admin.site.register(GroupFile)
admin.site.register(Hotel)
admin.site.register(HotelType)
admin.site.register(Flight)
admin.site.register(FlightType)
admin.site.register(Itinerary)
admin.site.register(ItineraryDate)