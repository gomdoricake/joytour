from django.db import models
from guides.models import Guide

class Group(models.Model): 
    guide = models.ForeignKey('Guide', null=True, blank=True)
    driver = models.ForeignKey('Guide', null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    joycode = models.CharField(max_length=20, null=True, blank=True)
    agentcode = models.CharField(max_length=20, null=True, blank=True)
    agent_ref = models.CharField(max_length=30, null=True, blank=True)
    adt = models.PositiveIntegerField(null=True, blank=True)
    chd = models.PositiveIntegerField(null=True, blank=True)
    tc = models.PositiveIntegerField(null=True, blank=True)

    class Meta: 
        abstract = True

    def save(self, *args, **kwargs):
        if self.start_date: 
            year = str(self.start_date.year[2:])
            month = str(self.start_date.month)
            day = str(self.start_date.day)
        else: 
            year, month, day = '00', '00', '00'

        group_or_fit = ""
        if self.adt + self.chd + self.tc <= 9:
            group_or_fit = "F"
        else: 
            group_or_fit = "G"

        self.joycode = self.agentcode + day + month + year + group_or_fit

        super().save(*args, **kwargs)


class GroupFile(Group):
    hotel = models.CharField(max_lenth=30, null=True, blank=True)
    meeting_board = models.CharField(max_length=30, null=True, blank=True)


class Itinerary(models.Model): 
    groupfile = models.ForeignKey(GroupFile, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    schedule = models.CharField(max_length=50, null=True, blank=True)
    time = models.TimeField()
    memo = models.CharField(max_length=100, null=True, blank=True)
    payment = models.CharField(max_length=10, null=True, blank=True)


class Invoice(Group): 
    meal_total = models.DecimalField(max_digit=10, decimal_places=2, null=True, blank=True)
    attraction_total = models.DecimalField(max_digit=10, decimal_places=2, null=True, blank=True)
    vehicle_total = models.DeimalField(max_digit=10, decimal_places=2, null=True, blank=True)
    guide_invoice_total = models.DecimalField(max_digit=10, decimal_places=2, null=True, blank=True)
    operation_total = models.DecimalField(max_digit=10, decimal_places=2, null=True, blank=True)
    grand_total = models.DecimalField(max_digit=10, decimal_places=2, null=True, blank=True)
    

class Meal(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    meal_type = models.CharField(max_lenth=20, null=True, blank=True)
    price_adt = models.DecimalField(max_digit=10, decimal_places=2, null=True, blank=True)
    price_chd = models.DecimalField(max_digit=10, decimal_places=2, null=True, blank=True)
    price_total = models.DecimalField(max_digit=10, decimal_places=2, null=True, blank=True)

class Attraction(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    attraction_type = models.CharField(max_length=20, null=True, blank=True)
    price_adt = models.DecimalField(max_digit=10, decimal_places=2, null=True, blank=True)
    price_chd = models.DecimalField(max_digit=10, decimal_places=2, null=True, blank=True)
    price_total = models.DecimalField(max_digit=10, decimal_places=2, null=True, blank=True)

class Vehicle(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    vehicle_type = models.CharField(max_length=20, null=True, blank=True)
    seat = models.CharField(max_length=10, null=True, blank=True)
    price_total = models.DecimalField(max_digit=10, decimal_places=2, null=True, blank=True)
    # 12인승, 21인승, 48인승이냐에 따라 가격이 달라지도록

class GuideInvoice(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    guide_invoice_type = models.CharField(max_length=20, null=True, blank=True)
    price_total = models.DecimalField(max_digit=10, decimal_places=2, null=True, blank=True)
    
class Tip(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    guide_tip = models.DecimalField(max_digit=10, decimal_places=2, null=True, blank=True)
    driver_tip = models.DecimalField(max_digit=10, decimal_places=2, null=True, blank=True)
    price_total = models.DecimalField(max_digit=10, decimal_places=2, null=True, blank=True)
