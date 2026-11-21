from django import forms
from django.forms import formset_factory
from inbound.models import Group, Agent, GroupFile, Itinerary, HotelType, FlightType, ItineraryDate


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

class GroupFileForm(forms.ModelForm): 
    class Meta: 
        model = GroupFile
        fields = ['meeting_board']


class HotelTypeForm(forms.ModelForm): 
    class Meta: 
        model = HotelType
        fields = ['hotel_name', 'address']

class HotelForm(forms.Form): 
    hoteltype = forms.ModelChoiceField(
        queryset=HotelType.objects.all(), 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    confirm_num = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    room_type = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )    

class FlightTypeForm(forms.ModelForm): 
    class Meta: 
        model = FlightType
        fields = ['region_code']

class FlightForm(forms.Form):
    itinerary_date =  forms.ModelChoiceField(
        queryset=ItineraryDate.objects.all(), 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    flight_code = room_type = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    ) 
    time = room_type = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    ) 
    from_flight_type = forms.ModelChoiceField(
        queryset=FlightType.objects.all(), 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    to_flight_type = forms.ModelChoiceField(
        queryset=FlightType.objects.all(), 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tour_guide = room_type = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    ) 

class ItineraryDateForm(forms.ModelForm): 
    class Meta: 
        model = ItineraryDate
        fields = ['date']    
        widgets = {
            'time': forms.DateInput(attrs={'type': 'date'}),
        }
        
class ItineraryForm(forms.ModelForm): 
    class Meta: 
        model = Itinerary
        fields = ['schedule', 'time', 'memo', 'payment']
        widgets = {
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

ItineraryFormSet = formset_factory(
    ItineraryForm,
    extra=0
)

from invoices.models import MealType

class GroupFileMealForm(forms.Form):
    itinerary_date = forms.ModelChoiceField(
        queryset=ItineraryDate.objects.all(), 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    ) 
    groupfile_meal_type = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    mealtype =  forms.ModelChoiceField(
        queryset=MealType.objects.all(), 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    note = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    