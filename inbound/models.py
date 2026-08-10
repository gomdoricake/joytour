from django.db import models
from guides.models import Guide

class Agent(models.Model): 
    code = models.CharField(max_length=10, null=True, blank=True)
    name = models.CharField(max_length=30, null=True, blank=True)
    abn = models.CharField(max_length=30, null=True, blank=True)
    tel = models.CharField(max_length=30, null=True, blank=True)
    email = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return str(self.code)


class Group(models.Model): 
    guide = models.ForeignKey(Guide, null=True, blank=True, on_delete=models.SET_NULL, related_name='%(class)s_guides')
    driver = models.ForeignKey(Guide, null=True, blank=True, on_delete=models.SET_NULL, related_name='%(class)s_drivers')
    agent = models.ForeignKey(Agent, null=True, blank=True, on_delete=models.SET_NULL, related_name='%(class)s_agents')
    start_date = models.DateField(null=True, blank=True)
    joycode = models.CharField(max_length=20, null=True, blank=True)
    agent_ref = models.CharField(max_length=30, null=True, blank=True)
    adt = models.PositiveIntegerField(null=True, blank=True)
    chd = models.PositiveIntegerField(null=True, blank=True)
    tc = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.start_date: 
            year = f"{self.start_date.year:04d}"[2:]
            month = f"{self.start_date.month:02d}"
            day = f"{self.start_date.day:02d}"
        else: 
            year, month, day = '00', '00', '00'

        group_or_fit = ""

        adt_val = self.adt or 0
        chd_val = self.chd or 0
        tc_val = self.tc or 0

        if adt_val + chd_val + tc_val <= 9:
            group_or_fit = "F"
        else: 
            group_or_fit = "G"

        agentcode = self.agent.code if self.agent else ""
        self.joycode = agentcode + day + month + year + group_or_fit

        super().save(*args, **kwargs)




class GroupFile(Group):
    hotel = models.CharField(max_length=30, null=True, blank=True)
    meeting_board = models.CharField(max_length=30, null=True, blank=True)


class Itinerary(models.Model): 
    groupfile = models.ForeignKey(GroupFile, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    schedule = models.CharField(max_length=50, null=True, blank=True)
    time = models.TimeField()
    memo = models.CharField(max_length=100, null=True, blank=True)
    payment = models.CharField(max_length=10, null=True, blank=True)


class Invoice(Group): 
    meal_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    attraction_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vehicle_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    guide_invoice_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    operation_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)    

class Meal(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    meal_type = models.CharField(max_length=20, null=True, blank=True)
    price_adt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_chd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

class Attraction(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    attraction_type = models.CharField(max_length=20, null=True, blank=True)
    price_adt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_chd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

class Vehicle(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    vehicle_type = models.CharField(max_length=20, null=True, blank=True)
    seat = models.CharField(max_length=10, null=True, blank=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # 12인승, 21인승, 48인승이냐에 따라 가격이 달라지도록

class GuideInvoice(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    guide_invoice_type = models.CharField(max_length=20, null=True, blank=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
class Tip(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    guide_tip = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    driver_tip = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
