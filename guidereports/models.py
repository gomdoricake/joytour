from django.db import models
from guides.models import Guide

class GuideReport(models.Model):
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name='reports')
    group_code = models.CharField(max_length=100)
    report_date = models.DateField()
    guide_fee = models.TextField()
    guide_exp = models.TextField()
    attraction_exp = models.TextField()
    restaurant_exp = models.TextField()
    fuel_exp = models.TextField()
    other_exp = models.TextField()

    def __str__(self):
        return f"{self.guide_name} - {self.group_code}"