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
    eventcode = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'list': 'eventcode_datalist', 
            'placeholder': '선택하거나 직접 입력하세요', 
            'class': 'form-control'
        })
    ) 
    class Meta: 
        model = Event
        fields = ['report_date', 'eventcode']
        labels = {
            'report_date': 'Report Date', 
        }
        widgets = {
            'report_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'}
            ),
        }
    

class GuideExpForm(forms.ModelForm): 
    class Meta:
        model = GuideExp
        fields = ['expense_type', 'expense', 'memo']
        widgets = {
            'expense': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
        }


class AgencyPaxForm(forms.ModelForm): 
    class Meta: 
        model = GuideReport
        fields = ['agency_code', 'coach', 'adt', 'chd', 'tc']
        labels = {
            'agency_code': 'Agency Code',
            'coach': 'Coach',
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
        self.fields['agency_code'].widget = forms.TextInput(attrs = {
            'list': 'agency_datalist', 
            'placeholder': '선택하거나 직접 입력하세요', 
            'class': 'form-control'
        })


class InboundEventForm(forms.ModelForm):
    eventcode = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'list': 'eventcode_datalist', 
            'placeholder': '선택하거나 직접 입력하세요', 
            'class': 'form-control'
        })
    ) 
    hours = forms.ChoiceField(
        choices=INBOUND_HOURS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Event
        fields = ['report_date', 'eventcode', 'hours', 'overtime', 'coach_start_time', 'coach_end_time']
        widgets = {
            'report_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'}
            ),
            'coach_start_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'coach_end_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
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
    expense_type = forms.CharField(
        widget=forms.TextInput(attrs={
            'list': 'restaurant_datalist', 
            'placeholder': '선택하거나 직접 입력하세요', 
            'class': 'form-control'
        })
    ) 
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
        fields = ['report_date', 'expense_type', 'memo', 'adt', 'chd', 'tc', 'tg', 'tod']
        labels = {
            'report_date': 'Report Date', 
            'expense_type': 'Expense Type'
        }
        widgets = {
            'report_date': forms.DateInput(attrs={'type': 'date'}),
            'expense_type': forms.Select(attrs={'class': 'form-control'})
        }


class FuelExpForm(forms.ModelForm): 

    file_key = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta: 
        model = FuelExp
        fields = ['report_date', 'expense', 'memo', 'file_key']
        labels = {
            'report_date': 'Report Date', 
            'expense': 'Expense',
            'memo': 'Memo'
        }
        widgets = {
            'report_date': forms.DateInput(attrs={'type': 'date'}),
        }