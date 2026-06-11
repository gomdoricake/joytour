from django import apps
from django import forms
from .models import GuideReport
from .rate import DAY_EVENTCODE_12SEAT, DAY_EVENTCODE_GUIDE_ONLY, DAY_EVENTCODE_OTHERS, INBOUND_EVENTCODE

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
    eventcode = forms.ChoiceField(choices=[], label='Event Code', required=True)
    class Meta: 
        model = GuideReport
        fields = ['guide_exp', 'attraction_exp', 'restaurant_exp', 'fuel_exp', 'other_exp']
        labels = {
            'guide_exp': 'Guide Expense', 
            'attraction_exp': 'Attraction Expense', 
            'restaurant_exp': 'Restaurant Expense',
            'fuel_exp': 'Fuel Expense', 
            'other_exp': 'Other Expense'
        }
        widgets = {
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

    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)


        self.field_order=['eventcode']


        if self.instance:
            role = self.instance.role
            day_inbound = self.instance.day_inbound
            print('role' + role + 'day_inbound' + day_inbound)

            if day_inbound == 'DAY' and role == '12 SEAT':
                print("DAY 12 SEAT !!!") 
                self.fields['eventcode'].choices = DAY_EVENTCODE_12SEAT
            elif day_inbound == 'DAY' and role == 'GUIDE ONLY': 
                self.fields['eventcode'].choices = DAY_EVENTCODE_GUIDE_ONLY
            elif day_inbound == 'DAY': 
                self.fields['eventcode'].choices = DAY_EVENTCODE_OTHERS
            
            if day_inbound == 'INBOUND': 
                self.fields['eventcode'].choices = INBOUND_EVENTCODE 

