from django import forms
from ..models import PkquoteInfo

class PkquoteForm(forms.ModelForm):

    class Meta:
        model = PkquoteInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkquoteForm,self).__init__(*args, **kwargs)

        self.fields['qt_updated_by'].empty_label = "--Select--"
