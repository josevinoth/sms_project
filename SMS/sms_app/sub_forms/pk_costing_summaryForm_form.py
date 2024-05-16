from django import forms
from ..models import PkpurchaseorderInfo,PkcostingsummaryInfo

class PkcostingsummaryForm(forms.ModelForm):

    class Meta:
        model = PkcostingsummaryInfo
        fields = '__all__'

    def clean_unique_field(self):
        cs_assessment_num_val = self.cleaned_data.get('cs_assessment_num')
        print(cs_assessment_num_val)
        if PkcostingsummaryInfo.objects.filter(cs_assessment_num=cs_assessment_num_val).exists():
            raise forms.ValidationError("This value already exists.")
        return cs_assessment_num_val

    def __init__(self, *args, **kwargs):
        super(PkcostingsummaryForm,self).__init__(*args, **kwargs)
        self.fields['cs_assessment_num'].empty_label = "--Select--"
        self.fields['cs_updated_by'].empty_label = "--Select--"
        self.fields['cs_customer_po'].empty_label = "--Select--"
