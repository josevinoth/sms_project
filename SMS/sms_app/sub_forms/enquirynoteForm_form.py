from django import forms
from ..models import EnquirynoteInfo

class EnquirynoteaddForm(forms.ModelForm):

    class Meta:
        model = EnquirynoteInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EnquirynoteaddForm,self).__init__(*args, **kwargs)
        self.fields['en_customername'].empty_label = "--Select--"
        self.fields['en_customerdepartment'].empty_label = "--Select--"
        self.fields['en_vehiclecategory'].empty_label = "--Select--"
        self.fields['en_vehicletype'].empty_label = "--Select--"
        self.fields['en_assignedto'].empty_label = "--Select--"
        self.fields['en_status'].empty_label = "--Select--"
        self.fields['en_fromlocaion'].empty_label = "--Select--"
        self.fields['en_tolocation'].empty_label = "--Select--"