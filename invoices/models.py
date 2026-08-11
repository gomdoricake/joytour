from django.db import models
from inbound.models import Group

class Invoice(Group): 
    meal_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    attraction_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vehicle_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    guide_invoice_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
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
    meal = models.ManyToManyField(Meal, related_name='mealtype')
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
