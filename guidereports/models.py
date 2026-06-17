from django.db import models
from django.apps import apps
from guides.models import Guide
from .rate import *
from datetime import datetime
from django.core.exceptions import ValidationError


class GuideReport(models.Model):
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name='guidereports')
    day_inbound = models.CharField(max_length=100, choices=DAY_INBOUND)
    role = models.CharField(max_length=100, choices=ROLE)
    group_code = models.CharField(max_length=100, blank=True, null=True)
    agency_code = models.CharField(max_length=10, choices=AGENCY_CHOICES, blank=True, null=True) 
    final_guide_fee = models.TextField()

    def calculate_fee(self): 
        rate_mapping = {
            ('DAY', '12 SEAT'): DAY_RATE_12SEAT,
            ('DAY', '21 SEAT'): DAY_RATE_21SEAT,
            ('DAY', '53 SEAT'): DAY_RATE_53SEAT,
            ('DAY', 'GUIDE ONLY'): DAY_RATE_GUIDE_ONLY,
            ('INBOUND', '12 SEAT'): INBOUND_RATE_12SEAT,
            ('INBOUND', 'GUIDE ONLY'): INBOUND_RATE_GUIDE_ONLY,
        }
        target_rate_dict = rate_mapping.get((self.day_inbound, self.role))
        if not target_rate_dict:
            return 0.00
        
        if self.pk: 
            Event = apps.get_model('guidereports', 'Event')
            related_events = Event.objects.filter(guidereport=self)

            if related_events.exists(): 
                representative_event = related_events.first()
                
                if representative_event.report_date:
                    if isinstance(representative_event.report_date, str):
                        date_obj = datetime.strptime(representative_event.report_date, '%Y-%m-%d').date()
                        today_str = date_obj.strftime('%d%m%y')
                    else:
                        today_str = representative_event.report_date.strftime('%d%m%y')
                
                eventcode = representative_event.eventcode
                
                if eventcode in target_rate_dict:
                    rate_list = target_rate_dict[eventcode]
                    
                    if self.guide and hasattr(self.guide, 'grade') and self.guide.grade:
                        grade_index = self.guide.grade - 1
                        if 0 <= grade_index < len(rate_list):
                            return rate_list[grade_index]
        else:
            print("가이드 리포트의 PK가 없어 이벤트를 조회할 수 없습니다. (0.00 반환)")

        return 0.00
class Event(models.Model): 
    eventcode = models.CharField(max_length=10)
    report_date = models.DateField()
    guidereport = models.ForeignKey(GuideReport, on_delete=models.CASCADE, related_name='events')
    guide_fee = models.TextField()

    def __str__(self): 
        return self.eventcode
    
class GuideExp(models.Model): 
    EXPENSE_CHOICES = [
        ('WASH', 'Car Wash'),
        ('FUEL', 'Fuel'),
        ('PARK', 'Parking'),
        ('OTHER', 'ETC'),
    ]
    guide_report = models.ForeignKey(GuideReport, on_delete=models.CASCADE, related_name='expenses')
    expense_type = models.CharField(max_length=10, choices=EXPENSE_CHOICES, default='WASH') 
    expense = models.DecimalField(max_digits=10, decimal_places=2) 

    def __str__(self): 
        return str(self.expense_type) + " " + str(self.expense)
    
class RestaurantExp(models.Model): 
    EXPENSE_CHOICES = [
        ('40', 'BANG POP'), 
        ('30', 'LA PORCHETTA'), 
        ('25', '홍대'),
        ('25', '대장금'),
        ('OTHERS', 'OTHERS')
    ]
    guide_report = models.ForeignKey(GuideReport, on_delete=models.CASCADE, related_name='restaurants')
    expense_type = models.CharField(max_length=100, choices=EXPENSE_CHOICES, default='홍대'),
    
    def __str__(self): 
        return self.expense_type

class AttractionExp(models.Model): 
    EXPENSE_CHOICES = [
        ('34', 'EUREKA'), 
        ('40', 'PENGUINE PARADE'), 
    ]
    guide_report = models.ForeignKey(GuideReport, on_delete=models.CASCADE, related_name='attractions')
    expense_type = models.CharField(max_length=100, choices=EXPENSE_CHOICES, default='EUREKA')

    def __str__(self): 
        return self.expense_type