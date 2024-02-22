from django import forms
from ..models import User_extInfo

class registrationaddForm(forms.ModelForm):

    class Meta:
        model = User_extInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(registrationaddForm,self).__init__(*args, **kwargs)
        self.fields['role'].empty_label = "--Select--"
