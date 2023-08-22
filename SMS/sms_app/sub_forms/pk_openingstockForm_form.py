from django import forms
from ..models import PkopeningstockInfo

class PkopeningstockForm(forms.ModelForm):

    class Meta:
        model = PkopeningstockInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkopeningstockForm,self).__init__(*args, **kwargs)
        self.fields['os_category'].empty_label = "--Select--"
        self.fields['os_stock_type'].empty_label = "--Select--"
        self.fields['os_type_of_wood'].empty_label = "--Select--"
        self.fields['os_source'].empty_label = "--Select--"
        self.fields['os_updated_by'].empty_label = "--Select--"
