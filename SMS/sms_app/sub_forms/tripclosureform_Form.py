from django import forms
from ..models import TripclosureInfo

class TripclosureaddForm(forms.ModelForm):

    class Meta:
        model = TripclosureInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(TripclosureaddForm,self).__init__(*args, **kwargs)
        self.fields['tc_financestatus'].empty_label = "--Select--"
