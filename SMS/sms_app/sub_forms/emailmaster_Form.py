from django import forms
from ..models import EnquirynoteInfo
from ..sub_models.emailmaster_mod import Emailmaster


class EmailmasterForm(forms.ModelForm):

    class Meta:
        model = Emailmaster
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EmailmasterForm,self).__init__(*args, **kwargs)
        self.fields['em_emailtype'].empty_label = "--Select--"
        self.fields['em_Customer_name'].empty_label = "--Select--"
        self.fields['em_customerdepartment'].empty_label = "--Select--"



