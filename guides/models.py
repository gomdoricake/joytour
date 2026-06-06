from django.db import models
from django.contrib.auth.models import User # 장고 내장 유저 모델

class Guide(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='guide_profile', null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    init_training_date = models.DateField(null=True, blank=True)
    init_super_date = models.DateField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    grade = models.IntegerField(null=True, blank=True)
    abn = models.CharField(max_length=20, null=True, blank=True)
    contact_info = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    bank_account_name = models.CharField(max_length=100, null=True, blank=True)
    bsb = models.CharField(max_length=6, null=True, blank=True)
    account_number = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name

    