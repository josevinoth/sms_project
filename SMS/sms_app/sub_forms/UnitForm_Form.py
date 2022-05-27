from django import forms
from ..models import UnitInfo

class UnitaddForm(forms.ModelForm):
    class Meta:
        model = UnitInfo
        fields = '__all__'

    #def __init__(self, *args, **kwargs):
        #super(CityaddForm,self).__init__(*args, **kwargs)
        #self.fields['country'].empty_label = "--Select--"
        #self.fields['state'].empty_label = "--Select--"