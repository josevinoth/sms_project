from django import forms
from ..models import Sales_target_info

class SalestargetaddForm(forms.ModelForm):
    class Meta:
        model = Sales_target_info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SalestargetaddForm,self).__init__(*args, **kwargs)
        self.fields['st_sales_person'].empty_label = "--Select--"