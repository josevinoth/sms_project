from django import forms
from ..models import Currency_type

class CurrencytypeaddForm(forms.ModelForm):
    class Meta:
        model = Currency_type
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super(CurrencytypeaddForm,self).__init__(*args, **kwargs)
    #     self.fields['country'].empty_label = "--Select--"
    #     self.fields['state'].empty_label = "--Select--"