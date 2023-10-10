from django import forms
from ..models import TripdetailInfo

class TripdetailaddForm(forms.ModelForm):
    tr_vehicletype_selection_requested = forms.BooleanField(initial=True,required=False)
    tr_vehicletype_selection_placed = forms.BooleanField(required=False)

    tc_tripcost = forms.FloatField(required=False)
    tc_parkingcost = forms.FloatField(required=False)
    tc_tollcost = forms.FloatField(required=False)
    tc_loadingcost = forms.FloatField(required=False)
    tc_unloadingcost = forms.FloatField(required=False)
    tc_weighmentcost = forms.FloatField(required=False)
    tc_handlingcost = forms.FloatField(required=False)
    tc_pod = forms.FloatField(required=False)
    class Meta:
        model = TripdetailInfo
        # fields = '__all__'
        fields = ['tr_enquirynumber','tr_consignmentnumber','tr_tripnumber','tr_vehiclesource','tr_vehicletype','tr_vehicletype_placed','tr_vehicletype_selection_requested','tr_vehicletype_selection_placed','tr_vehiclenumber','tr_drivername','tr_driver_lic','tr_drivernumber','tr_departedlocation','tr_departedkm','tr_departeddate','tr_reportedlocation','tr_reportedkm','tr_reporteddate','tc_financestatus','tr_updated_by','tr_category','tr_remarks','tr_loading_time','tr_unloading_time']
    def __init__(self, *args, **kwargs):
        super(TripdetailaddForm,self).__init__(*args, **kwargs)
        self.fields['tr_consignmentnumber'].empty_label = "--Select--"
        self.fields['tr_vehiclesource'].empty_label = "--Select--"
        self.fields['tr_vehicletype_placed'].empty_label = "--Select--"
        self.fields['tr_vehicletype'].empty_label = "--Select--"
        self.fields['tr_vehiclenumber'].empty_label = "--Select--"
        self.fields['tr_departedlocation'].empty_label = "--Select--"
        self.fields['tr_reportedlocation'].empty_label = "--Select--"
        self.fields['tc_financestatus'].empty_label = "--Select--"
        self.fields['tr_category'].empty_label = "--Select--"