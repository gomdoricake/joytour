from django.contrib import admin
from .models import Guide
from guidereports.models import GuideReport
# Register your models here.

class GuideReportInline(admin.TabularInline):
    model = GuideReport
    extra = 0
    
    fields = ['group_code'] 

class GuideAdmin(admin.ModelAdmin):
    inlines = [GuideReportInline]

admin.site.register(Guide, GuideAdmin)
