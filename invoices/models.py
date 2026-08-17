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

class MealType(models.Model): 
    name = models.CharField(max_length=30, null=True, blank=True)
    price_adt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_chd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   
    def __str__(self):
        return str(self.name)

class Meal(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='meals')
    meal_type = models.ForeignKey(MealType, on_delete=models.SET_NULL, related_name='meals', null=True, blank=True)
    restaurant = models.CharField(null=True, blank=True )
    date = models.DateField(null=True, blank=True)
    price_adt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_chd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self): 
        return str(self.invoice.joycode) + ": " + str(self.restaurant)

class AttractionType(models.Model): 
    name = models.CharField(max_length=30, null=True, blank=True)
    price_adt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_chd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_tc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   
    def __str__(self):
        return str(self.name)


class Attraction(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='attractions')
    attraction_type = models.ForeignKey(AttractionType, on_delete=models.SET_NULL, related_name='attractions', null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    attraction_name = models.CharField(max_length=20, null=True, blank=True)
    price_adt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_chd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_tc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return str(self.invoice.joycode) + ": " + str(self.attraction_type)


class VehicleType(models.Model): 
    seat = models.CharField(max_length=10, null=True, blank=True)
    location = models.CharField(max_length=30, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return str(self.seat) + ": " + str(self.location)


class Vehicle(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, related_name='vehicles', null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    vehicle_name = models.CharField(max_length=40, null=True, blank=True)
    seat = models.CharField(max_length=10, null=True, blank=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # 12인승, 21인승, 48인승이냐에 따라 가격이 달라지도록
    def __str__(self):
        return str(self.date) + ': ' + str(self.vehicle_type)


class GuideInvoiceType(models.Model): 
    location = models.CharField(max_length=30, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return str(self.location)


class GuideInvoice(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='guideinvoices')
    guideinvoice_type = models.ForeignKey(GuideInvoiceType, on_delete=models.SET_NULL, related_name='guideinvoices', null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    guideinvoice_name = models.CharField(max_length=20, null=True, blank=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return str(self.date) + ": " + str(self.guideinvoice_type)

    
class GuideTipType(models.Model): 
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return 'guide tip: ' + str(self.price)


class DriverTipType(models.Model): 
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return 'driver tip: ' + str(self.price)

class Tip(models.Model): 
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='tips')
    guidetip_type = models.ForeignKey(GuideTipType, on_delete=models.SET_NULL, related_name='guidetips', null=True, blank=True)
    drivertip_type = models.ForeignKey(DriverTipType, on_delete=models.SET_NULL, related_name='drivertips', null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    price_guidetip = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_drivertip = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return str(self.date) + ' $' + str(self.price_total)


