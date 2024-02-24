from django import forms
from ..models import City

class CityaddForm(forms.ModelForm):
    class Meta:
        model = City
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CityaddForm,self).__init__(*args, **kwargs)
        self.fields['country'].empty_label = "--Select--"
        self.fields['state'].empty_label = "--Select--"