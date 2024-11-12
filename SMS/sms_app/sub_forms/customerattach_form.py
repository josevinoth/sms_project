from django import forms
from ..models import Customerattach

class CustomerattachForm(forms.ModelForm):
    class Meta:
        model = Customerattach
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CustomerattachForm,self).__init__(*args, **kwargs)
        self.fields['ca_customer_name'].empty_label = "--Select--"
        self.fields['ca_updated_by'].empty_label = "--Select--"
        self.fields['ca_status'].empty_label = "--Select--"