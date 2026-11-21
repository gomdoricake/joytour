from django import forms
from django.forms import formset_factory, modelformset_factory
from .models import Meal, MealType, Attraction, AttractionType, Vehicle, VehicleType, \
            GuideInvoice, GuideInvoiceType, GuideTipType, DriverTipType


class MealTypeForm(forms.ModelForm): 
    class Meta: 
        model = MealType
        fields = ['name', 'price_adt', 'price_chd', 'description']

class MealForm(forms.Form): 
    mealtype = forms.ModelChoiceField(
        queryset = MealType.objects.all(), 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    pax_adt = forms.IntegerField(
        min_value = 0, 
        required=False,
        widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'enter'})
    )
    price_adt = forms.DecimalField( 
        label='ADT price',
        required=False,           
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'})
    )
    pax_chd = forms.IntegerField(
        min_value = 0, 
        required=False,
        widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'enter'})
    )
    price_chd = forms.DecimalField( 
        label='CHD price',
        required=False,           
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'})
    )

    def clean(self): 
        cleaned_data = super().clean()

        pax_adt = cleaned_data.get('pax_adt') or 0
        pax_chd = cleaned_data.get('pax_chd') or 0

        cleaned_data['pax_adt'] = pax_adt
        cleaned_data['pax_chd'] = pax_chd

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
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    pax_adt = forms.IntegerField(
        min_value = 0, 
        required=False,
        widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'enter'})
    )
    price_adt = forms.DecimalField( 
        label='ADT price',
        required=False,           
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'})
    )
    pax_chd = forms.IntegerField(
        min_value = 0, 
        required=False,
        widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'enter'})
    )

    price_chd = forms.DecimalField( 
        label='CHD price',
        required=False,           
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'})
    )

    def clean(self): 
        cleaned_data = super().clean()

        adt = cleaned_data.get('adt') or 0
        chd = cleaned_data.get('chd') or 0

        cleaned_data['adt'] = adt
        cleaned_data['chd'] = chd

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
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    price_total = forms.DecimalField(        
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
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.DateField(
        required=False,
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



class GuideTipTypeForm(forms.ModelForm): 
    class Meta: 
        model = GuideTipType
        fields = ['price']
    

class DriverTipTypeForm(forms.ModelForm): 
    class Meta: 
        model = DriverTipType
        fields = ['price']



class TipForm(forms.Form): 

    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    guidetiptype = forms.ModelChoiceField(
        queryset = GuideTipType.objects.all(), 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    drivertiptype = forms.ModelChoiceField(
        queryset = DriverTipType.objects.all(), 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

        
TipFormSet = formset_factory(
    TipForm,
    extra=0
)

