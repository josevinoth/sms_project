from django import forms
from django.db import models
from ..models import PkneedassessmentInfo, PkquotationsummaryInfo

class PkquotationsummaryForm(forms.ModelForm):
    class Meta:
        model = PkquotationsummaryInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        na_id = kwargs.pop('na_id', None)
        super(PkquotationsummaryForm, self).__init__(*args, **kwargs)
        self.fields['qs_assessment_num'].empty_label = "--Select--"
        #  Get assessments where quotation already completed
        completed_assessments = PkquotationsummaryInfo.objects.filter(qs_status_id=5).values_list('qs_assessment_num_id', flat=True)
        
        #  Show only assessments NOT completed in quotation summary (but allow current one if updating)
        qs = PkneedassessmentInfo.objects.exclude(id__in=completed_assessments)
        if self.instance and self.instance.pk:
            qs = PkneedassessmentInfo.objects.filter(models.Q(id__in=qs) | models.Q(id=self.instance.qs_assessment_num_id))
        elif na_id:
            # Include the na_id assessment so it can be pre-selected from "Convert to Quotation"
            qs = PkneedassessmentInfo.objects.filter(models.Q(id__in=qs) | models.Q(id=na_id))
        
        self.fields['qs_assessment_num'].queryset = qs.order_by('-id')
        self.fields['qs_updated_by'].empty_label = "--Select--"
        self.fields['qs_status'].empty_label = "--Select--"
