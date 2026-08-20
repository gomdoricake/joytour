from django import forms
from django.forms import formset_factory
from inbound.models import Group, Agent, GroupFile, Itinerary


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



class GroupFileForm(forms.Form): 
    hotel = forms.CharField(max_length=30)
    meeting_board = forms.CharField(max_length=30)


class ItineraryForm(forms.ModelForm): 
    class Meta: 
        model = Itinerary
        fields = ['date', 'schedule', 'time', 'memo', 'payment']
        widgets = {
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

ItineraryFormSet = formset_factory(
    ItineraryForm,
    extra=0
)

