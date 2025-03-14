
from django import forms
from ..models import Gatein_pre_info

class gateinpre_mblForm(forms.ModelForm):
    class Meta:
        model = Gatein_pre_info
        fields = ['gatein_pre_branch', 'gatein_pre_status', 'gatein_pre_shipment_att', 'gatein_pre_cust_appr_att', 'gatein_pre_updated_by']

    def __init__(self, *args, **kwargs):
        super(gateinpre_mblForm,self).__init__(*args, **kwargs)
        self.fields['gatein_pre_branch'].empty_label = "--Select--"
        self.fields['gatein_pre_status'].empty_label = "--Select--"
        self.fields['gatein_pre_updated_by'].empty_label = "--Select--"