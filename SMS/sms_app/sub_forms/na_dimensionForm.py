from django import forms
from ..models import Nadimension

class NadimensionForm(forms.ModelForm):
    class Meta:
        model = Nadimension
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(NadimensionForm,self).__init__(*args, **kwargs)
        self.fields['nad_assess_num'].empty_label = "--Select--"