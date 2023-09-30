from django import forms
from ..models import Places

class PlacesForm(forms.ModelForm):
    class Meta:
        model = Places
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PlacesForm,self).__init__(*args, **kwargs)
        self.fields['city'].empty_label = "--Select--"