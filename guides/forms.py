from django import apps
from django import forms
from .models import Guide

class GuideProfileForm(forms.ModelForm):
    class Meta:
        model = Guide
        # 💡 유저에게 직접 입력받을 필드만 지정합니다. (user는 뷰에서 자동으로 채울 겁니다)
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