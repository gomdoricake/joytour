from django.db import models
from guidereports.rate import *
# Create your models here.


class GuideFeeRate(models.Model):
    grade = models.PositiveIntegerField()
    day_inbound = models.CharField(max_length=100, choices=DAY_INBOUND)
    event_code_or_hours = models.CharField(max_length=100)
    seat_type_or_fit_or_group = models.CharField(max_length=100)
    is_sponsored = models.BooleanField(default=False)
    guidefee = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Grade: {self.grade}, Day/Inbound: {self.day_inbound}, Event Code/Hours: {self.event_code_or_hours}, Seat Type or FIT or GROUP: {self.seat_type_or_fit_or_group}, Sponsored: {self.is_sponsored}, Guide Fee: {self.guidefee}"