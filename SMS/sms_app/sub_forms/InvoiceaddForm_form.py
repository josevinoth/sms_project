from django import forms
from ..models import BilingInfo,Country,State,City

class InvoiceaddForm(forms.ModelForm):
    class Meta:
        model = BilingInfo
        fields ='__all__'

    def __init__(self, *args, **kwargs):
        super(InvoiceaddForm, self).__init__(*args, **kwargs)
        # self.fields['loc_country'].empty_label = "--Select--"
        # self.fields['loc_state'].empty_label = "--Select--"
        # self.fields['loc_city'].empty_label = "--Select--"
        # self.fields['loc_status'].empty_label = "--Select--"
