from django import forms
from ..models import Stockdescription

class StockdescriptionForm(forms.ModelForm):
    class Meta:
        model = Stockdescription
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(StockdescriptionForm, self).__init__(*args, **kwargs)
        self.fields['stock_type'].empty_label = "--Select--"
        self.fields['stock_received'].empty_label = "--Select--"
        self.fields['stock_Consumption'].empty_label = "--Select--"
