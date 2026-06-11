from django.db import models
from guides.models import Guide
from .rate import *
from datetime import datetime
class GuideReport(models.Model):
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name='reports')
    day_inbound = models.CharField(max_length=100, choices=DAY_INBOUND)
    role = models.CharField(max_length=100, choices=ROLE)
    eventcode = models.CharField(max_length=100, null=True, blank=True)
    group_code = models.CharField(max_length=100, blank=True, null=True)
    report_date = models.DateField()
    guide_fee = models.TextField()
    guide_exp = models.TextField(null=True, blank=True)
    attraction_exp = models.TextField(null=True, blank=True)
    restaurant_exp = models.TextField(null=True, blank=True)
    fuel_exp = models.TextField(null=True, blank=True)
    other_exp = models.TextField(null=True, blank=True)

    def calculate_fee(self): 
        target_rate_dict = None

        if self.day_inbound == 'DAY' and self.role == '12 SEAT':
            target_rate_dict = DAY_RATE_12SEAT
        elif self.day_inbound == 'DAY' and self.role == '21 SEAT': 
            target_rate_dict = DAY_RATE_21SEAT
        elif self.day_inbound == 'DAY' and self.role == '53 SEAT':
            target_rate_dict = DAY_RATE_53SEAT
        elif self.day_inbound == 'DAY' and self.role == 'GUIDE ONLY':
            target_rate_dict = DAY_RATE_GUIDE_ONLY
        elif self.day_inbound == 'INBOUND'and self.role == '12 SEAT':
            target_rate_dict = INBOUND_RATE_12SEAT
        elif self.day_inbound == 'INBOUND' and self.role == 'GUIDE ONLY':
            target_rate_dict = INBOUND_RATE_GUIDE_ONLY

        today_str = ""
        if self.report_date:
            if isinstance(self.report_date, str):
                date_obj = datetime.strptime(self.report_date, '%Y-%m-%d').date()
                today_str = date_obj.strftime('%d%m%y')
            else:
                today_str = self.report_date.strftime('%d%m%y')

        if target_rate_dict and self.eventcode in target_rate_dict:
            rate_list = target_rate_dict[self.eventcode]
            
            final_rate = rate_list[self.guide.grade - 1] 
            print('guide grade: ' + str(self.guide.grade))
            print("final_rate: " + str(final_rate))
            return final_rate

        return 0.00      

    def save(self, *args, **kwargs): 
        if not self.group_code: 
            today_str = ""
            if self.report_date:
                if isinstance(self.report_date, str):
                    date_obj = datetime.strptime(self.report_date, '%Y-%m-%d').date()
                    today_str = date_obj.strftime('%d%m%y')
                else:
                    today_str = self.report_date.strftime('%d%m%y')

            day_inbound = str(self.day_inbound).upper().strip() if self.day_inbound else ""
            eventcode = str(self.eventcode).strip() if self.eventcode else ""

            if day_inbound == "DAY" and today_str and eventcode: 
                self.group_code = 'J' + today_str + eventcode
                
        super().save(*args, **kwargs)                

    def __str__(self):
        return f"{self.guide.name} - {self.group_code}"

class EventCode(models.Model): 
    eventcode = models.CharField(max_length=10)
    guidereport = models.ForeignKey(GuideReport, on_delete=models.CASCADE, related_name='eventcodes')

    def __str__(self): 
        return self.eventcode