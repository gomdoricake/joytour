from django import forms
from inbound.models import Group, Agent


class AgentForm(forms.ModelForm): 
    class Meta: 
        model = Agent
        fields = ['code', 'name', 'abn', 'tel', 'email', 'operation_fee']
        labels = {
            'code': 'Agent Code',
            'name': 'Agent Name',
            'abn': 'ABN', 
            'tel': 'Telephone', 
            'email': 'Email',
            'operation_fee': 'Operation Fee'
        }


class GroupForm(forms.ModelForm):
    class Meta: 
        model = Group
        fields = ['guide', 'driver', 'start_date', 'agent', 'agent_ref', 'adt', 'chd', 'tc']
        labels = {
            'start_date': 'Report Date', 
            'agent': 'Agent Code', 
            'agent_ref': 'Agent Ref', 
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }
        