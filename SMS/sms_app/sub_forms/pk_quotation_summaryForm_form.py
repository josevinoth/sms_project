from django import forms
from ..models import PkquotationsummaryInfo

class PkquotationsummaryForm(forms.ModelForm):

    class Meta:
        model = PkquotationsummaryInfo
        fields = '__all__'

    def clean_unique_field(self):
        qs_assessment_num_val = self.cleaned_data.get('qs_assessment_num')
        print(qs_assessment_num_val)
        if PkquotationsummaryInfo.objects.filter(qs_assessment_num=qs_assessment_num_val).exists():
            raise forms.ValidationError("This value already exists.")
        return qs_assessment_num_val

    def __init__(self, *args, **kwargs):
        super(PkquotationsummaryForm,self).__init__(*args, **kwargs)
        self.fields['qs_assessment_num'].empty_label = "--Select--"
        self.fields['qs_updated_by'].empty_label = "--Select--"
