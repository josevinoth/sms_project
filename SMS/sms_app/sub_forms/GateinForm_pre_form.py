from django import forms
from django.forms import HiddenInput

from ..models import Gatein_pre_info,Gatein_pre_info_att

class Gatein_preaddForm(forms.ModelForm):
    class Meta:
        model = Gatein_pre_info
        # fields = '__all__'
        fields = ['gatein_pre_number','gatein_pre_branch','gatein_pre_transporter','gatein_pre_truck_number','gatein_pre_truck_type','gatein_pre_driver','gatein_pre_contact_number','gatein_pre_DL_number','gatein_pre_arrival_date_time','gatein_pre_otl','gatein_pre_status','gatein_pre_updated_by']

    def __init__(self, *args, **kwargs):
        super(Gatein_preaddForm, self).__init__(*args, **kwargs)
        self.fields['gatein_pre_truck_type'].empty_label = "--Select--"
        self.fields['gatein_pre_status'].empty_label = "--Select--"
        self.fields['gatein_pre_branch'].empty_label = "--Select--"

class Gatein_pre_att_addForm(forms.ModelForm):
    # dam_OTL_pic = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    gatein_pre_number_att = forms.CharField(widget=HiddenInput(), required=False)
    gatein_pre_shipment_att = forms.FileField(required=False)
    gatein_pre_cust_appr_att = forms.FileField(required=False)
    class Meta:
        model = Gatein_pre_info_att
        fields = '__all__'
        # fields=('dam_OTL_pic','dam_document')