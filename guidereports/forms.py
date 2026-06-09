from django import forms
from .models import GuideReport


class GuideReportForm(forms.ModelForm):
    class Meta:
        model = GuideReport

        fields = ['guide', 'group_code', 'report_date', 'guide_fee', 'guide_exp', 'attraction_exp',
                    'restaurant_exp', 'fuel_exp', 'other_exp'] 
        labels = {
            'guide': 'Name', 
            'group_code': 'Group Code', 
            'report_date': 'Report Date',
            'guide_fee': 'Guide Fee', 
            'guide_exp': 'Guide Exp', 
            'attraction_exp': 'Attraction Exp', 
            'restaurant_exp': 'Restaurant Exp', 
            'fuel_exp': 'Fuel Exp', 
            'other_exp': 'Other Ex'
        }