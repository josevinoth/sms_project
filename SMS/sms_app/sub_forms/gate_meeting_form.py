from django import forms
from ..models import Gatemeetinginfo

class GatemeetingaddForm(forms.ModelForm):
    class Meta:
        model = Gatemeetinginfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(GatemeetingaddForm, self).__init__(*args, **kwargs)
        self.fields['gm_branch'].empty_label = "--Select--"
        self.fields['gm_unit'].empty_label = "--Select--"
        self.fields['gm_Previous_day_WH_closing_checklist'].empty_label = "--Select--"
        self.fields['gm_Current_day_WH_opening_checklist'].empty_label = "--Select--"
        self.fields['gm_WMS_updation_till_yesterday'].empty_label = "--Select--"
        self.fields['gm_DSR_sent_to_all_customers_yesterday'].empty_label = "--Select--"
        self.fields['gm_Stock_informed_to_Customer'].empty_label = "--Select--"
        self.fields['gm_Pre_alerts_customers_inbound_outbound'].empty_label = "--Select--"
        self.fields['gm_Inbound_documents_scanned'].empty_label = "--Select--"
        self.fields['gm_Outbound_documents_scanned'].empty_label = "--Select--"
        self.fields['gm_Cleanliness_of_warehouse'].empty_label = "--Select--"
        self.fields['gm_Facility_checklist_provided'].empty_label = "--Select--"
        self.fields['gm_Space_issues'].empty_label = "--Select--"
        self.fields['gm_HPTE_condition'].empty_label = "--Select--"
        self.fields['gm_Fork_Lift_check'].empty_label = "--Select--"
        self.fields['gm_Weight_scale_condition'].empty_label = "--Select--"
        self.fields['gm_Fire_Extinguisher'].empty_label = "--Select--"
        self.fields['gm_Fork_Lift_check'].empty_label = "--Select--"
        self.fields['gm_CCTV_condition'].empty_label = "--Select--"
        self.fields['gm_Lights_condition'].empty_label = "--Select--"
        self.fields['gm_UPS_invertor_condition'].empty_label = "--Select--"
        self.fields['gm_Genset_condition'].empty_label = "--Select--"
        self.fields['gm_Stock_of_Diesel_Genset'].empty_label = "--Select--"
