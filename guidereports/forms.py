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

    def clean(self):
        cleaned_data = super().clean()
        report_type = cleaned_data.get("type")
        role = cleaned_data.get("role")

        if report_type == 'Inbound':
            allowed_roles = ['12 SEAT', 'GUIDE ONLY']
            if role not in allowed_roles:
                raise forms.ValidationError(f"Inbound인 경우 Role은 {allowed_roles} 중 하나여야 합니다.")
        
        return cleaned_data

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
        fields = ['expense_type', 'expense', 'memo']
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
        fields = ['agency_code', 'adt', 'chd', 'tc']
        labels = {
            'agency_code': 'Agency Code',
            'adt': 'ADT', 
            'chd': 'CHD',
            'tc': 'TC', 
        }
        widgets = {
            'adt': forms.NumberInput(attrs={'placeholder': '0'}),
            'chd': forms.NumberInput(attrs={'placeholder': '0'}),
            'tc': forms.NumberInput(attrs={'placeholder': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['adt', 'tc', 'chd']:
            if self.instance and getattr(self.instance, field_name) == 0:
                self.fields[field_name].initial = None
            
            self.fields[field_name].widget.attrs['placeholder'] = ''

class InboundEventForm(forms.ModelForm): 
    eventcode = forms.ChoiceField(
        choices=INBOUND_EVENTCODE,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    hours = forms.ChoiceField(
        choices=INBOUND_HOURS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Event
        fields = ['report_date', 'eventcode', 'hours']
        widgets = {
            'report_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hours'].required = True
        
        if self.data:
            prefix = self.prefix
            eventcode = self.data.get(f'{prefix}-eventcode')
            if eventcode == 'AM/AS':
                self.hours = None
                self.fields['hours'].required = False

class RestaurantExpForm(forms.ModelForm): 
    class Meta: 
        model = RestaurantExp
        fields = ['report_date','expense_type', 'memo']
        labels = {
            'report_date': 'Report Date',
            'expense_type': 'Expense Type'
        }
        widgets = {
            'report_date': forms.DateInput(attrs={'type': 'date'}),
            'expense_type': forms.Select(attrs={'class': 'form-control'})
        }
    
class AttractionExpForm(forms.ModelForm):
    class Meta: 
        model = AttractionExp
        fields = ['report_date', 'expense_type', 'memo']
        labels = {
            'report_date': 'Report Date', 
            'expense_type': 'Expense Type'
        }
        widgets = {
            'report_date': forms.DateInput(attrs={'type': 'date'}),
            'expense_type': forms.Select(attrs={'class': 'form-control'})
        }

class FuelExpForm(forms.ModelForm): 
    class Meta: 
        model = FuelExp
        fields = ['report_date', 'expense', 'memo']
        labels = {
            'report_date': 'Report Date', 
            'expense': 'Expense',
            'memo': 'Memo'
        }
        widgets = {
            'report_date': forms.DateInput(attrs={'type': 'date'}),
        }
