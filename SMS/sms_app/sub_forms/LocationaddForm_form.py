from django import forms
from ..models import Location_info,Country,State,City

class LocationaddForm(forms.ModelForm):
    class Meta:
        model = Location_info
        fields ='__all__'

    def __init__(self, *args, **kwargs):
        super(LocationaddForm, self).__init__(*args, **kwargs)
        self.fields['loc_country'].empty_label = "--Select--"
        self.fields['loc_state'].empty_label = "--Select--"
        self.fields['loc_city'].empty_label = "--Select--"
        self.fields['loc_status'].empty_label = "--Select--"

