from django.db import models
from django.apps import apps
from guides.models import Guide
from .rate import *
from datetime import datetime
from django.core.exceptions import ValidationError
from storages.backends.s3boto3 import S3Boto3Storage


class GuideReport(models.Model):
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name='guidereports')
    is_confirmed = models.BooleanField(default=False, null=True, blank=True)
    is_paid = models.BooleanField(default=False, null=True, blank=True) 
    pay_status = models.CharField(max_length=10, null=True, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    invoice_number = models.CharField(max_length=10, null=True, blank=True)
    day_inbound = models.CharField(max_length=100, choices=DAY_INBOUND)
    role = models.CharField(max_length=100)
    coach = models.CharField(max_length=100, null=True, blank=True)
    group_code = models.CharField(max_length=100, blank=True, null=True)
    agency_code = models.CharField(max_length=100, blank=True, null=True) 
    adt = models.PositiveIntegerField(default=0)
    tc = models.PositiveIntegerField(default=0, null=True, blank=True)    
    chd = models.PositiveIntegerField(default=0, null=True, blank=True)
    final_events_fee = models.TextField(null=True, blank=True)
    final_retaurants_fee = models.TextField(null=True, blank=True)
    final_attractions_fee = models.TextField(null=True, blank=True)
    final_expenses_fee = models.TextField(null=True, blank=True)
    final_fuels_fee = models.TextField(null=True, blank=True)
    final_amount_due = models.TextField(null=True, blank=True)
    super_ann = models.TextField(null=True, blank=True)
    is_printed = models.BooleanField(default=False, null=True, blank=True)
                    
    def __str__(self): 
        return str(self.guide.name) + ': ' + str(self.group_code)

class Event(models.Model): 
    eventcode = models.CharField(max_length=100)
    report_date = models.DateField()
    hours = models.CharField(max_length=10, choices=INBOUND_HOURS,null=True,blank=True)
    guidereport = models.ForeignKey(GuideReport, on_delete=models.CASCADE, related_name='events')
    guide_fee = models.TextField()
    overtime = models.PositiveIntegerField(default=0, null=True, blank=True)
    coach_start_time = models.TimeField(null=True, blank=True)
    coach_end_time = models.TimeField(null=True, blank=True)

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
            ('INBOUND', 'FIT'): INBOUND_RATE_12SEAT,
            ('INBOUND', 'GROUP'): INBOUND_RATE_GUIDE_ONLY,
        }

        sponsored_rate_mapping = {
            ('DAY', '12 SEAT'): SPONSORED_DAY_RATE_12SEAT,
            ('DAY', '21 SEAT'): SPONSORED_DAY_RATE_21SEAT,
            ('DAY', '53 SEAT'): SPONSORED_DAY_RATE_53SEAT,
            ('DAY', 'GUIDE ONLY'): SPONSORED_DAY_RATE_GUIDE_ONLY,
            ('INBOUND', 'FIT'): SPONSORED_INBOUND_RATE_12SEAT,
            ('INBOUND', 'GROUP'): SPONSORED_INBOUND_RATE_GUIDE_ONLY,
        }

        if guide_profile.is_sponsored: 
            target_rate_dict = sponsored_rate_mapping.get((day_inbound_val, role_val))
        else: 
            target_rate_dict = rate_mapping.get((day_inbound_val, role_val))
        calculated_fee = "0.00"

        if day_inbound_val == "DAY" and target_rate_dict: 
            current_code = self.eventcode

        elif day_inbound_val == "INBOUND" and target_rate_dict:
            if self.hours == None:
                current_code = 'AM/AS'
            else: 
                current_code = self.hours

        if current_code in target_rate_dict:
            rate_list = target_rate_dict[current_code]
            if guide_profile and hasattr(guide_profile, 'grade') and guide_profile.grade:
                grade_index = guide_profile.grade - 1
                if 0 <= grade_index < len(rate_list):
                    calculated_fee = float(rate_list[grade_index])

        self.guide_fee = calculated_fee
        super().save(*args, **kwargs)

    def __str__(self): 
        return self.eventcode


class GuideExp(models.Model): 
    guide_report = models.ForeignKey(GuideReport, on_delete=models.CASCADE, related_name='expenses')
    expense_type = models.CharField(max_length=10, default='WASH') 
    expense = models.DecimalField(max_digits=10, decimal_places=2, default=0.0) 
    memo = models.CharField(max_length=30, null=True, blank=True)
    file_key = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self): 
        return str(self.expense_type) + " " + str(self.expense)
    

from django.utils import timezone

class RestaurantExp(models.Model): 
    guide_report = models.ForeignKey(GuideReport, on_delete=models.CASCADE, related_name='restaurants')
    report_date = models.DateField(null=True, blank=True)
    expense_type = models.CharField(max_length=100, blank=True, default='')
    expense = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    memo = models.CharField(max_length=30, null=True, blank=True)
    adt = models.PositiveIntegerField(default=0, null=True, blank=True)
    chd = models.PositiveIntegerField(default=0, null=True, blank=True)
    tc = models.PositiveIntegerField(default=0, null=True, blank=True)
    tg = models.PositiveIntegerField(default=0, null=True, blank=True)
    dr = models.PositiveIntegerField(default=0, null=True, blank=True)
    
    def __str__(self): 
        return str(self.expense_type)

class AttractionExp(models.Model): 
    guide_report = models.ForeignKey(GuideReport, on_delete=models.CASCADE, related_name='attractions')
    report_date = models.DateField(null=True, blank=True)
    expense_type = models.CharField(max_length=100, blank=True, default='')
    expense = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    memo = models.CharField(max_length=30, null=True, blank=True)
    adt = models.PositiveIntegerField(default=0, null=True, blank=True)
    chd = models.PositiveIntegerField(default=0, null=True, blank=True)
    tc = models.PositiveIntegerField(default=0, null=True, blank=True)
    tod = models.PositiveIntegerField(default=0, null=True, blank=True)
    tg = models.PositiveIntegerField(default=0, null=True, blank=True)

    def __str__(self): 
        return str(self.expense_type)

class FuelExp(models.Model): 
    guide_report = models.ForeignKey(GuideReport, on_delete=models.CASCADE, related_name='fuels')
    report_date = models.DateField(null=True, blank=True)
    expense = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)
    memo = models.CharField(max_length=30, null=True, blank=True)
    file_key = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self): 
        return str(self.report_date) + str(self.guide_report.group_code)