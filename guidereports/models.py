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

    def __str__(self): 
        return str(self.guide.name) + ': ' + str(self.group_code)

class Event(models.Model): 
    eventcode = models.CharField(max_length=10)
    report_date = models.DateField()
    guidereport = models.ForeignKey(GuideReport, on_delete=models.CASCADE, related_name='events')
    guide_fee = models.TextField()

    def save(self, *args, **kwargs): 
        parent = self.guidereport
        
        day_inbound_val = str(parent.day_inbound).upper().strip() if parent.day_inbound else ""
        role_val = str(parent.role).upper().strip() if parent.role else ""
        guide_profile = parent.guide

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
            if self.eventcode == 'AM/AS':
                current_code = 'AM/AS'
            else: 
                current_code = '10HRS'

            
            if current_code in target_rate_dict:
                rate_list = target_rate_dict[current_code]

                print("rate_list: " + str(rate_list))
                
                if guide_profile and hasattr(guide_profile, 'grade') and guide_profile.grade:
                    grade_index = guide_profile.grade - 1
                    if 0 <= grade_index < len(rate_list):
                        calculated_fee = float(rate_list[grade_index])

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
    memo = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self): 
        return str(self.expense_type) + " " + str(self.expense)
    
class RestaurantExp(models.Model): 
    EXPENSE_CHOICES = [
        ('홍대', '홍대'),
        ('대장금', '대장금'),
        ('OAK & VINE', 'OAK & VINE'),  
        ('CELLAR DOOR', 'CELLAR DOOR'), 
        ('LA PORCHETTA', 'LA PORCHETTA'), 
        ('FUSION SPACE', 'FUSION SPACE'), 
        ('FEAST BUFFET', 'FEAST BUFFET'), 
        ('BANG POP', 'BANG POP'),
        ('WING LOCK', 'WING LOCK'),
        ('ROCHFORD', 'ROCHFORD'),
        ('OTHERS', 'OTHERS')
    ]
    guide_report = models.ForeignKey(GuideReport, on_delete=models.CASCADE, related_name='restaurants')
    report_date = models.DateField(null=True, blank=True)
    expense_type = models.CharField(max_length=100, choices=EXPENSE_CHOICES, default='홍대')
    expense = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    memo = models.CharField(max_length=30, null=True, blank=True)

    def save(self, *args, **kwargs):
        price_mapping = {
            'BANG POP': 40,
            'LA PORCHETTA': 30,
            '홍대': 25,
            '대장금': 25,
            'OTHERS': 0.00,
        }
        
        self.expense = price_mapping.get(self.expense_type, 0.00)
        
        super().save(*args, **kwargs)
    
    def __str__(self): 
        return str(self.expense_type)

class AttractionExp(models.Model): 
    EXPENSE_CHOICES = [
        ('PUFFING BILLY', 'PUFFING BILLY'), 
        ('PENGUIN PARADE', 'PENGUIN PARADE'), 
        ('PENINSULA', 'PENINSULA'), 
        ('HELI 15min', 'HELI 15min'), 
        ('PENGUINE PARADE', 'PENGUINE PARADE'), 
        ('CRUISE', 'CRUISE'), 
        ('EUREKA', 'EUREKA'), 
        ('WINE TASTING', 'WINE TASTING')
    ]
    guide_report = models.ForeignKey(GuideReport, on_delete=models.CASCADE, related_name='attractions')
    report_date = models.DateField(null=True, blank=True)
    expense_type = models.CharField(max_length=100, choices=EXPENSE_CHOICES, default='EUREKA')
    expense = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    memo = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self): 
        return self.expense_type

class FuelExp(models.Model): 
    guide_report = models.ForeignKey(GuideReport, on_delete=models.CASCADE, related_name='fuels')
    report_date = models.DateField(null=True, blank=True)
    expense = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    memo = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self): 
        return str(self.guide_report.report_date) + str(self.guide_report.group_code)