from django import forms
from django.db import models
from ..models import PkneedassessmentInfo,PkpurchaseorderInfo

class PkpurchaseorderForm(forms.ModelForm):

    class Meta:
        model = PkpurchaseorderInfo
        exclude = ['sales_order_num', 'po_updated_by']
        widgets = {
            'po_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'po_validity_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        na_id = kwargs.pop('na_id', None)
        super(PkpurchaseorderForm,self).__init__(*args, **kwargs)
        self.fields['po_assessment_num'].empty_label = "--Select--"
        qs = PkneedassessmentInfo.objects.filter(na_status=5)
        if self.instance and self.instance.pk and self.instance.po_assessment_num_id:
            qs = PkneedassessmentInfo.objects.filter(models.Q(id__in=qs) | models.Q(id=self.instance.po_assessment_num_id))
        elif na_id:
            qs = PkneedassessmentInfo.objects.filter(models.Q(id__in=qs) | models.Q(id=na_id))
        self.fields['po_assessment_num'].queryset = qs.order_by('-id')
        self.fields['po_customer_name'].empty_label = "--Select--"
        self.fields['po_status'].empty_label = "--Select--"
