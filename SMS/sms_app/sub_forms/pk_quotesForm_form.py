from django import forms
from ..models import PkquotesInfo

class PkquotesForm(forms.ModelForm):

    class Meta:
        model = PkquotesInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkquotesForm,self).__init__(*args, **kwargs)
        self.fields['qt_updated_by'].empty_label = "--Select--"
