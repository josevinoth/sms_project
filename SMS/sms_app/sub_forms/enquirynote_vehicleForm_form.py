from django import forms
from ..models import Enquirynotevehicle

class EnquirynotevehicleForm(forms.ModelForm):

    class Meta:
        model = Enquirynotevehicle
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EnquirynotevehicleForm,self).__init__(*args, **kwargs)
        self.fields['env_enquirynumber'].empty_label = "--Enquiry Number--"
        self.fields['env_vehicletype'].empty_label = "--Vehicle Type--"
        self.fields['env_vehiclecategory'].empty_label = "--Vehicle Category--"
        self.fields['env_updated_by'].empty_label = "--Select--"
