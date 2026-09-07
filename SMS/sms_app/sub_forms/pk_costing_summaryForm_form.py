from django import forms
from django.db import models
from ..models import PkneedassessmentInfo,PkcostingsummaryInfo

class PkcostingsummaryForm(forms.ModelForm):

    class Meta:
        model = PkcostingsummaryInfo
        fields = [
            'cs_assessment_num', 'cs_customer_name', 'cs_customer_new_name', 
            'cs_customer_po', 'cs_invoice_num', 'cs_job_no', 'cs_wood_cost', 'cs_plywood_cost',
            'cs_engineer_cost', 'cs_labour_cost', 'cs_crane_cost', 'cs_ht_cost', 
            'cs_management_cost', 'cs_material_cost', 'cs_transport_cost', 
            'cs_total_cost_wom', 'cs_margin', 'cs_total_cost_wm', 'cs_gst', 
            'cs_final_cost', 'cs_total_cft', 'cs_rate_per_cft', 'cs_total_sqft', 'cs_status', 
            'cs_pack_type', 'cs_address', 'cs_cost_includes', 'cs_notes', 
            'cs_terms_condition', 'cs_client_scope', 'cs_bvm_scope', 
            'cs_others_cost', 'cs_others_description', 'cs_updated_by'
        ]

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
