from django import forms
from ..models import Enquirynotevehicle

class EnquirynotevehicleForm(forms.ModelForm):

    class Meta:
        model = Enquirynotevehicle
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EnquirynotevehicleForm,self).__init__(*args, **kwargs)
        self.fields['env_enquirynumber'].widget = forms.HiddenInput()
        self.fields['env_vehicletype'].empty_label = "--Vehicle Type--"
        self.fields['env_vehiclecategory'].empty_label = "--Vehicle Category--"
        self.fields['env_updated_by'].empty_label = "--Select--"
        self.fields['env_quantity'].min_value = 1
        self.fields['env_quantity'].required = True
        if not self.instance.pk:
            self.initial['env_quantity'] = None
            self.fields['env_quantity'].initial = None

    def clean_env_quantity(self):
        quantity = self.cleaned_data.get('env_quantity')
        if quantity is None or quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return quantity
