from django import forms
from django.forms import formset_factory, modelformset_factory
from .models import Meal, MealType, Attraction, AttractionType, Vehicle, VehicleType, GuideInvoice, GuideInvoiceType


class MealTypeForm(forms.ModelForm): 
    class Meta: 
        model = MealType
        fields = ['name', 'price_adt', 'price_chd']

class MealForm(forms.Form): 
    mealtype = forms.ModelChoiceField(
        queryset = MealType.objects.all(), 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    adt = forms.IntegerField(
        min_value = 0, 
        required=False,
        widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'enter'})
    )
    chd = forms.IntegerField(
        min_value = 0, 
        required=False,
        widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'enter'})
    )
    tc = forms.IntegerField(
        min_value = 0, 
        required=False,
        widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'enter'})
    )

    def clean(self): 
        cleaned_data = super().clean()

        adt = cleaned_data.get('adt') or 0
        chd = cleaned_data.get('chd') or 0
        tc = cleaned_data.get('tc') or 0

        cleaned_data['adt'] = adt
        cleaned_data['chd'] = chd
        cleaned_data['tc'] = tc

        return cleaned_data

MealFormSet = formset_factory(
    MealForm, 
    extra=0
)

class AttractionTypeForm(forms.ModelForm): 
    class Meta: 
        model = AttractionType
        fields = ['name', 'price_adt', 'price_chd', 'price_tc']


class AttractionForm(forms.Form): 
    attractiontype = forms.ModelChoiceField(
        queryset = AttractionType.objects.all(), 
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    adt = forms.IntegerField(
        min_value = 0, 
        required=False,
        widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'enter'})
    )
    chd = forms.IntegerField(
        min_value = 0, 
        required=False,
        widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'enter'})
    )
    tc = forms.IntegerField(
        min_value = 0, 
        required=False,
        widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'enter'})
    )

    def clean(self): 
        cleaned_data = super().clean()

        adt = cleaned_data.get('adt') or 0
        chd = cleaned_data.get('chd') or 0
        tc = cleaned_data.get('tc') or 0

        cleaned_data['adt'] = adt
        cleaned_data['chd'] = chd
        cleaned_data['tc'] = tc

        return cleaned_data


AttractionFormSet = formset_factory(
    AttractionForm,
    extra=0
)


class VehicleTypeForm(forms.ModelForm): 
    class Meta: 
        model = VehicleType
        fields = ['seat', 'location', 'price']


class VehicleForm(forms.Form): 
    vehicle_type = forms.ModelChoiceField(
        queryset = VehicleType.objects.all(), 
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    price = forms.DecimalField(        
        max_digits=8,
        decimal_places=2,
        required=False,
        min_value=0.01,
        max_value=999999.99
    )


VehicleFormSet = formset_factory(
    VehicleForm,
    extra=0
)


class GuideInvoiceTypeForm(forms.ModelForm): 
    class Meta: 
        model = GuideInvoiceType
        fields = ['location', 'price']


class GuideInvoiceForm(forms.Form): 
    guideinvoice_type = forms.ModelChoiceField(
        queryset = GuideInvoiceType.objects.all(), 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    price = forms.DecimalField(        
        max_digits=8,
        decimal_places=2,
        required=False,
        min_value=0.01,
        max_value=999999.99
    )


GuideInvoiceFormSet = formset_factory(
    GuideInvoiceForm,
    extra=0
)


