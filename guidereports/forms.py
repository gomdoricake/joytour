from django import apps
from django import forms
from .models import *
from .rate import DAY_EVENTCODE_12SEAT, DAY_EVENTCODE_GUIDE_ONLY, DAY_EVENTCODE_21SEAT, DAY_EVENTCODE_53SEAT, INBOUND_EVENTCODE

class GuideReportMainForm(forms.ModelForm):
    class Meta:
        model = GuideReport
        fields = ['day_inbound', 'role']
        labels = {
            'day_inbound': 'Day Inbound', 
            'role': 'Role', 
        }

class GuideReportDayForm(forms.ModelForm): 

    eventcode = forms.ChoiceField(choices=[], label='Event Code', required=True)
    class Meta: 
        model = Event
        fields = ['report_date']
        labels = {
            'report_date': 'Report Date', 
        }
        widgets = {
            'report_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)

        self.field_order=['eventcode']

        if self.instance:
            role = self.instance.role
            day_inbound = self.instance.day_inbound
            print('role' + role + 'day_inbound' + day_inbound)

            if role == '12 SEAT':
                self.fields['eventcode'].choices = DAY_EVENTCODE_12SEAT
            if role == '21 SEAT': 
                self.fields['eventcode'].choices = DAY_EVENTCODE_21SEAT
            if role == '53 SEAT': 
                self.fields['eventcode'].choices = DAY_EVENTCODE_53SEAT
            elif role == 'GUIDE ONLY': 
                self.fields['eventcode'].choices = DAY_EVENTCODE_GUIDE_ONLY

class GuideExpForm(forms.ModelForm): 
    class Meta:
        model = GuideExp
        fields = ['expense_type', 'expense']
        widgets = {
            'expense': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
        }


class GuideReportInboundForm(forms.ModelForm): 

    event = forms.ChoiceField(choices=[], label='Event', required=True)
    class Meta: 
        model = Event
        fields = ['report_date']
        labels = {
            'report_date': 'Report Date', 
        }
        widgets = {
            'report_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)

        self.field_order=['eventcode']

        if self.instance:
            role = self.instance.role
            day_inbound = self.instance.day_inbound
            print('role' + role + 'day_inbound' + day_inbound)

            self.fields['eventcode'].choices = INBOUND_EVENTCODE

class AgencyPaxForm(forms.ModelForm): 
    class Meta: 
        model = GuideReport
        fields = ['agency_code', 'adt', 'tc', 'chd']
        labels = {
            'agency_code': 'Agency Code',
            'adt': 'ADT', 
            'tc': 'TC', 
            'chd': 'CHD'
        }

class InboundEventForm(forms.ModelForm): 
    eventcode = forms.ChoiceField(
        choices=INBOUND_EVENTCODE,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Event
        fields = ['report_date', 'eventcode']
        widgets = {
            'report_date': forms.DateInput(attrs={'type': 'date'}),
        }


class RestaurantExpForm(forms.ModelForm): 
    class Meta: 
        model = RestaurantExp
        fiels = ['expense_type']
        widgets = {
            'expense_type': forms.Select(attrs={'class': 'form-control'})
        }