from django import forms
from ..models import State

class StateaddForm(forms.ModelForm):
    class Meta:
        model = State
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(StateaddForm,self).__init__(*args, **kwargs)
        self.fields['country'].empty_label = "--Select--"