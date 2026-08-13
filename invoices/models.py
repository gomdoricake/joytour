from django.db import models
from inbound.models import Group

class Invoice(Group): 
    meal_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    attraction_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vehicle_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    guide_invoice_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tip_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    operation_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)   

    def __str__(self):
        return str(self.joycode) 


class Meal(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    restaurant = models.CharField(null=True, blank=True )
    date = models.DateField(null=True, blank=True)
    price_adt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_chd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self): 
        return str(self.invoice.joycode) + ": " + str(self.restaurant)


class MealType(models.Model): 
    meal = models.ManyToManyField(Meal, related_name='mealtype', blank=True, null=True)
    name = models.CharField(max_length=30, null=True, blank=True)
    price_adt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_chd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   
    def __str__(self):
        return str(self.name)


class Attraction(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    attraction_type = models.CharField(max_length=20, null=True, blank=True)
    price_adt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_chd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_tc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return str(self.invoice.joycode) + ": " + str(self.attraction_type)


class AttractionType(models.Model): 
    attraction = models.ManyToManyField(Attraction, related_name='attractiontype', blank=True, null=True)
    name = models.CharField(max_length=30, null=True, blank=True)
    price_adt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_chd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_tc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   
    def __str__(self):
        return str(self.name)
 

class Vehicle(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    vehicle_type = models.CharField(max_length=40, null=True, blank=True)
    seat = models.CharField(max_length=10, null=True, blank=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # 12인승, 21인승, 48인승이냐에 따라 가격이 달라지도록
    def __str__(self):
        return str(self.date) + ': ' + str(self.vehicle_type)


class VehicleType(models.Model): 
    vehicle = models.ManyToManyField(Vehicle, related_name='vehicletype', blank=True, null=True)
    seat = models.CharField(max_length=10, null=True, blank=True)
    location = models.CharField(max_length=30, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return str(self.seat) + ": " + str(self.location)


class GuideInvoice(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    guideinvoice_type = models.CharField(max_length=20, null=True, blank=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return str(self.date) + ": " + str(self.guideinvoice_type)


class GuideInvoiceType(models.Model): 
    guideinvoice = models.ManyToManyField(GuideInvoice, related_name='guideinvoicetype', blank=True, null=True)
    location = models.CharField(max_length=30, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return str(self.location)

    
class Tip(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    price_guidetip = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_drivertip = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return str(self.date) + ' $' + str(self.price_total)


class GuideTipType(models.Model): 
    tip = models.ManyToManyField(Tip, related_name='guidetiptype', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return 'guide tip: ' + str(self.price)


class DriverTipType(models.Model): 
    tip = models.ManyToManyField(Tip, related_name='drivertiptype', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return 'driver tip: ' + str(self.price)
