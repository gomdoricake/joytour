from django.db import models
from guides.models import Guide

class Agent(models.Model): 
    code = models.CharField(max_length=10, null=True, blank=True)
    name = models.CharField(max_length=30, null=True, blank=True)
    abn = models.CharField(max_length=30, null=True, blank=True)
    tel = models.CharField(max_length=30, null=True, blank=True)
    email = models.CharField(max_length=30, null=True, blank=True)
    operation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

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

        if not self.adt: self.adt = 0
        if not self.chd: self.chd = 0
        if not self.tc: self.tc = 0

        if self.adt + self.chd + self.tc <= 9:
            group_or_fit = "F"
        else: 
            group_or_fit = "G"

        agentcode = self.agent.code if self.agent else ""
        self.joycode = agentcode + day + month + year + group_or_fit

        super().save(*args, **kwargs)
    
    def __str__(self): 
        return f"{self.joycode}"




class GroupFile(models.Model):
    group = models.OneToOneField(Group, on_delete=models.SET_NULL, related_name='groupfile', null=True, blank=True)
    hotel = models.CharField(max_length=30, null=True, blank=True)
    meeting_board = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self): 
        if self.group: 
            return f"Group File {self.group.joycode}"
        else: 
            return f"."


class Itinerary(models.Model): 
    groupfile = models.ForeignKey(GroupFile, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    schedule = models.CharField(max_length=50, null=True, blank=True)
    time = models.TimeField()
    memo = models.CharField(max_length=100, null=True, blank=True)
    payment = models.CharField(max_length=10, null=True, blank=True)


