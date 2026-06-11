from django import apps
from django import forms
from .models import GuideReport
from .rate import *

class GuideReportStep1Form(forms.ModelForm):
    class Meta:
        model = GuideReport
        fields = ['day_inbound', 'role', 'report_date']
        labels = {
            'day_inbound': 'Day Inbound', 
            'role': 'Role', 
            'report_date': 'Report Date', 
        }
        widgets = {
            'report_date': forms.DateInput(attrs={'type': 'date'}),
        }

class GuideReportStep2Form(forms.ModelForm): 
    eventcode = forms.ChoiceField(choices=[], label='Event Code')

    class Meta: 
        model = GuideReport
        fields = ['guide_fee', 'guide_exp', 'attraction_exp', 'restaurant_exp', 'fuel_exp', 'other_exp']
        labels = {
            'guide_fee': 'Guide Fee', 
            'guide_exp': 'Guide Expense', 
            'attraction_exp': 'Attraction Expense', 
            'restaurant_exp': 'Restaurant Expense',
            'fuel_exp': 'Fuel Expense', 
            'other_exp': 'Other Expense'
        }
        widgets = {
            'guide_fee': forms.NumberInput(attrs={
                'step': 'any',
                'placeholder': 'Enter decimal value'
            }),
            'guide_exp': forms.NumberInput(attrs={
                'step': 'any',
                'placeholder': 'Enter decimal value'
            }),
            'attraction_exp': forms.NumberInput(attrs={
                'step': 'any',
                'placeholder': 'Enter decimal value'
            }),
            'restaurant_exp': forms.NumberInput(attrs={
                'step': 'any',
                'placeholder': 'Enter decimal value'
            }),
            'fuel_exp': forms.NumberInput(attrs={
                'step': 'any',
                'placeholder': 'Enter decimal value'
            }),
            'other_exp': forms.NumberInput(attrs={
                'step': 'any',
                'placeholder': 'Enter decimal value'
            }),
        }
