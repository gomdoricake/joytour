from django.db import models
from guides.models import Guide
from .rate import *
from django.utils import timezone

class GuideReport(models.Model):
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name='reports')
    day_inbound = models.CharField(max_length=100, choices=DAY_INBOUND)
    role = models.CharField(max_length=100, choices=ROLE)
    group_code = models.CharField(max_length=100, blank=True, null=True)
    report_date = models.DateField()
    guide_fee = models.TextField()
    guide_exp = models.TextField()
    attraction_exp = models.TextField()
    restaurant_exp = models.TextField()
    fuel_exp = models.TextField()
    other_exp = models.TextField()

    def save(self, *args, **kwargs): 
        if self.pk and not self.group_code: 
            today_str = timezone.now().strftime('%d%m%y')
            if self.day_inbound == "DAY": 
                self.group_code = 'J' + today_str + self.eventcodes.first().eventcode
        super().save(*args, **kwargs)
                

    def __str__(self):
        return f"{self.guide.name} - {self.group_code}"

class EventCode(models.Model): 
    eventcode = models.CharField(max_length=10)
    guidereport = models.ForeignKey(GuideReport, on_delete=models.CASCADE, related_name='eventcodes')

    def __str__(self): 
        return self.eventcode