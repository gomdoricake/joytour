from django.db import models

class Guide(models.Model):
    name = models.CharField(max_length=100)
    init_training_date = models.DateField()
    init_super_date = models.DateField()
    birth_date = models.DateField()
    grade = models.IntegerField()
    abn = models.CharField(max_length=20)
    contact_info = models.TextField()
    address = models.TextField()
    bank_account_name = models.CharField(max_length=100)
    bsb = models.CharField(max_length=6)
    account_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name

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
    