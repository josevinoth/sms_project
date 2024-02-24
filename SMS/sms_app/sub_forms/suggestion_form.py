from django import forms
from ..models import suggestioninfo

class queryaddForm(forms.ModelForm):

    class Meta:
        model = suggestioninfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(queryaddForm,self).__init__(*args, **kwargs)
        self.fields['raised_by'].empty_label = "--Select--"
        self.fields['suggestion_by'].empty_label = "--Select--"
