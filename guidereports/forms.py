from django import apps
from django import forms
from guidereports.models import GuideReport

class GuideReportForm(forms.ModelForm):
    class Meta:
        model = GuideReport
        fields = ['guide', 'day_inbound', 'role', 'group_code', 'report_date', 'guide_fee', 'guide_exp', 
                'attraction_exp', 'restaurant_exp', 'fuel_exp', 'other_exp']
        labels = {
            'guide': 'Guide', 
            'day_inbound': 'Day Inbound', 
            'role': 'Role', 
            'group_code': 'Group Code', 
            'report_date': 'Report Date', 
            'guide_fee': 'Guide Fee', 
            'guide_exp': 'Guide Expense', 
            'attraction_exp': 'Attraction Expense', 
            'restaurant_exp': 'Restaurant Expense',
            'fuel_exp': 'Fuel Expense', 
            'other_exp': 'Other Expense'
        }
        widgets = {
            'guide': forms.HiddenInput(),
            'report_date': forms.DateInput(attrs={'type': 'date'}),
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