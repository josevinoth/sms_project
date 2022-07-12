from django import forms
from ..models import Stock_type

class StocktypeaddForm(forms.ModelForm):
    class Meta:
        model = Stock_type
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super(CurrencytypeaddForm,self).__init__(*args, **kwargs)
    #     self.fields['country'].empty_label = "--Select--"
    #     self.fields['state'].empty_label = "--Select--"