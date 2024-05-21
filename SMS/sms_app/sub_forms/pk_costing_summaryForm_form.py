from django import forms
from ..models import PkneedassessmentInfo,PkcostingsummaryInfo

class PkcostingsummaryForm(forms.ModelForm):

    class Meta:
        model = PkcostingsummaryInfo
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(PkcostingsummaryForm,self).__init__(*args, **kwargs)
        self.fields['cs_assessment_num'].empty_label = "--Select--"
        self.fields['cs_assessment_num'].queryset = PkneedassessmentInfo.objects.filter(na_status=5).order_by('-id')
        self.fields['cs_updated_by'].empty_label = "--Select--"
        self.fields['cs_customer_po'].empty_label = "--Select--"
        self.fields['cs_status'].empty_label = "--Select--"
