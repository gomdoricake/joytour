from django import apps
from django import forms
from guides.models import Guide

class GuideProfileForm(forms.ModelForm):
    class Meta:
        model = Guide
        fields = ['name', 'init_training_date', 'birth_date', 'abn', 'contact_info', 'address',
                  'bank_account_name', 'bsb', 'account_number'] 
        labels = {
            'name': 'Name', 
            'init_training_date': 'Initial Training Date', 
            'birth_date': 'Birthday',
            'abn': 'ABN', 
            'contact_info': 'Contact Info', 
            'address': 'Address', 
            'bank_account_name': 'Bank Account Name', 
            'bsb': 'BSB', 
            'account_number': 'Account Number'
        }
