from django import forms
from django.db import models
from ..models import PkneedassessmentInfo,PkcostingsummaryInfo

class PkcostingsummaryForm(forms.ModelForm):

    class Meta:
        model = PkcostingsummaryInfo
        exclude = ['cs_updated_by']

    def __init__(self, *args, **kwargs):
        na_id = kwargs.pop('na_id', None)
        super(PkcostingsummaryForm,self).__init__(*args, **kwargs)
        self.fields['cs_assessment_num'].empty_label = "--Select--"
        qs = PkneedassessmentInfo.objects.filter(na_status=5)
        if self.instance and self.instance.pk and self.instance.cs_assessment_num_id:
            qs = PkneedassessmentInfo.objects.filter(models.Q(id__in=qs) | models.Q(id=self.instance.cs_assessment_num_id))
        elif na_id:
            qs = PkneedassessmentInfo.objects.filter(models.Q(id__in=qs) | models.Q(id=na_id))
        self.fields['cs_assessment_num'].queryset = qs.order_by('-id')
        self.fields['cs_customer_po'].empty_label = "--Select--"
        self.fields['cs_status'].empty_label = "--Select--"
