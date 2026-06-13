from django.contrib import admin
from .models import GuideReport, GuideExp, EventCode

admin.site.register(GuideReport)
admin.site.register(EventCode)
admin.site.register(GuideExp)