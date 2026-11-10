from django import forms
from .models import GuideFeeRate

class GuideFeeRateForm(forms.ModelForm):
    class Meta:
        model = GuideFeeRate
        fields = '__all__'
