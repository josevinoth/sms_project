from django import forms
from ..models import LocationmasterInfo

class LocationmasteraddForm(forms.ModelForm):
    class Meta:
        model = LocationmasterInfo
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(LocationmasteraddForm,self).__init__(*args, **kwargs)
        self.fields['lm_wh_location'].empty_label = "--Select--"