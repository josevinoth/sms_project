from django import forms
from ..models import PkquotationsummaryInfo

class PkquotationsummaryForm(forms.ModelForm):

    class Meta:
        model = PkquotationsummaryInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkquotationsummaryForm,self).__init__(*args, **kwargs)
        self.fields['qs_assessment_num'].empty_label = "--Select--"
        self.fields['qs_updated_by'].empty_label = "--Select--"
        self.fields['qs_status'].empty_label = "--Select--"
