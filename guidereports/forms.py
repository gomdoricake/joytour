from django import apps
from django import forms
from .models import GuideReport, GuideExp
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
        model = GuideReport
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

class GuideExpForm(forms.ModelForm): # 👈 이게 바로 원하시던 GuideExpForm 입니다!
    class Meta:
        model = GuideExp
        fields = ['expense_type', 'expense']
        widgets = {
            'expense': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
        }


class GuideReportInboundForm(forms.ModelForm): 

    eventcode = forms.ChoiceField(choices=[], label='Event Code', required=True)
    class Meta: 
        model = GuideReport
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
