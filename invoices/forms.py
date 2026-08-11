from django import forms
from django.forms import formset_factory, modelformset_factory
from .models import Meal, MealType, Attraction


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

AttractionFormSet = modelformset_factory(
    Attraction,
    fields=['date', 'attraction_type', 'price_adt', 'price_chd', 'price_total'],
    extra=0
)