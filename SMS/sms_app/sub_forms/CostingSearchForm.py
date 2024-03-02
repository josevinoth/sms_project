from django import forms
from ..models import Stockdescription,Pkstocktype

class CostingSearchForm(forms.Form):
    stock_type = forms.ModelChoiceField(
        queryset=Pkstocktype.objects.all(),
        empty_label='--Select--',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    stock_description = forms.ModelChoiceField(
        queryset=Stockdescription.objects.all(),
        empty_label='--Select--',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )


class ModifyDimensionsForm(forms.Form):
    modified_thick_height = forms.DecimalField(label='Modified Thick/Height')
    modified_width = forms.DecimalField(label='Modified Width')
    modified_length = forms.DecimalField(label='Modified Length')