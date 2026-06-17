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
    adt = models.PositiveIntegerField(default=0)
    tc = models.PositiveIntegerField(default=0)    
    chd = models.PositiveIntegerField(default=0)
    final_guide_fee = models.TextField()

class Event(models.Model): 
    eventcode = models.CharField(max_length=10)
    report_date = models.DateField()
    guidereport = models.ForeignKey(GuideReport, on_delete=models.CASCADE, related_name='events')
    guide_fee = models.TextField()

    def save(self, *args, **kwargs): 
        parent = self.guidereport
        
        day_inbound_val = str(parent.day_inbound).upper().strip() if parent.day_inbound else ""
        role_val = str(parent.role).upper().strip() if parent.role else ""
        guide_profile = parent.guide  # GuideReport에 연결된 가이드 프로필

        rate_mapping = {
            ('DAY', '12 SEAT'): DAY_RATE_12SEAT,
            ('DAY', '21 SEAT'): DAY_RATE_21SEAT,
            ('DAY', '53 SEAT'): DAY_RATE_53SEAT,
            ('DAY', 'GUIDE ONLY'): DAY_RATE_GUIDE_ONLY,
            ('INBOUND', '12 SEAT'): INBOUND_RATE_12SEAT,
            ('INBOUND', 'GUIDE ONLY'): INBOUND_RATE_GUIDE_ONLY,
        }
        
        target_rate_dict = rate_mapping.get((day_inbound_val, role_val))
        
        calculated_fee = "0.00"

        if target_rate_dict:
            current_code = self.eventcode
            
            if current_code in target_rate_dict:
                rate_list = target_rate_dict[current_code]
                
                if guide_profile and hasattr(guide_profile, 'grade') and guide_profile.grade:
                    grade_index = guide_profile.grade - 1
                    if 0 <= grade_index < len(rate_list):
                        calculated_fee = str(rate_list[grade_index])

        self.guide_fee = calculated_fee

        super().save(*args, **kwargs)

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
        ('BANG POP', 'BANG POP'), 
        ('LA PORCHETTA', 'LA PORCHETTA'), 
        ('홍대', '홍대'),
        ('대장금', '대장금'),
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