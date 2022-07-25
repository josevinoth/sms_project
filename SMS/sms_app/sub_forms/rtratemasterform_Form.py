from django import forms
from ..models import RtratemasterInfo

class RtratemasteraddForm(forms.ModelForm):

    class Meta:
        model = RtratemasterInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(RtratemasteraddForm,self).__init__(*args, **kwargs)
        self.fields['ro_fromlocation'].empty_label = "--Select--"
        self.fields['ro_tolocation'].empty_label = "--Select--"
        self.fields['ro_vehicletype'].empty_label = "--Select--"
        self.fields['ro_customer'].empty_label = "--Select--"
        self.fields['ro_customerdepartment'].empty_label = "--Select--"
