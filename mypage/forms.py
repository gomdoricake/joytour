from django import apps
from django import forms
from guides.models import Guide

class GuideProfileForm(forms.ModelForm):
    class Meta:
        model = Guide
        # 💡 유저에게 직접 입력받을 필드만 지정합니다. (user는 뷰에서 자동으로 채울 겁니다)
        fields = ['name', 'init_training_date', 'birth_date', 'abn', 'contact_info', 'address',
                  'bank_account_name', 'bsb', 'account_number'] 
        labels = {
            'name': '성함', 
            'init_training_date': '첫 트레이닝 날짜', 
            'birth_date': '생일',
            'abn': 'ABN', 
            'contact_info': '연락처', 
            'address': '주소', 
            'bank_account_name': '은행명', 
            'bsb': 'bsb', 
            'account_number': '계좌번호'
        }
        widgets = {
            'init_training_date': forms.DateInput(attrs={'type': 'date'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }