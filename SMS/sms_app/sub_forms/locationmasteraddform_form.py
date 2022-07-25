from django import forms
from django.core.exceptions import ValidationError

from ..models import LocationmasterInfo

class LocationmasteraddForm(forms.ModelForm):
    lm_concatenate = forms.CharField(error_messages={'unique': u'My custom message'})
    class Meta:
        model = LocationmasterInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(LocationmasteraddForm,self).__init__(*args, **kwargs)
        self.fields['lm_wh_location'].empty_label = "--Select--"
        self.fields['lm_wh_unit'].empty_label = "--Select--"
        self.fields['lm_areaside'].empty_label = "--Select--"
        self.fields['lm_customer_name'].empty_label = "--Select--"