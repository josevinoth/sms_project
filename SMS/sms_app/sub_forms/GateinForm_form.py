from django import forms
from ..models import Gatein_info

class GateinaddForm(forms.ModelForm):
    class Meta:
        model = Gatein_info
        fields = '__all__'
        # fields = ['gatein_job_no','gatein_invoice','gatein_customer','gatein_customer_type','gatein_arrival_date','gatein_department','gatein_shipper','gatein_consignee','gatein_no_of_pkg','gatein_weight','gatein_driver','gatein_contact_number','gatein_DL_number','gatein_otl','gatein_transporter','gatein_truck_number','gatein_truck_type','gatein_status','gatein_pre_id','gatein_updated_by']

    def __init__(self, *args, **kwargs):
        super(GateinaddForm, self).__init__(*args, **kwargs)
        self.fields['gatein_driver'].empty_label = "--Select--"
        self.fields['gatein_status'].empty_label = "--Select--"
        self.fields['gatein_customer'].empty_label = "--Select--"
        self.fields['gatein_department'].empty_label = "--Select--"
        self.fields['gatein_customer_type'].empty_label = "--Select--"
        self.fields['gatein_pre_id'].empty_label = "--Select--"
        self.fields['gatein_updated_by'].empty_label = "--Select--"
        self.fields['gatein_comodity'].empty_label = "--Select--"
