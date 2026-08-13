from django import forms
from ..models import TripdetailInfo,Trip_closure_files_Info

class TripclosureaddForm(forms.ModelForm):
    customer_name = forms.CharField(label="Customer Name", required=False, disabled=True)
    trip_date = forms.CharField(label="Trip Date", required=False, disabled=True)
    tc_handlingcost_reason = forms.CharField(required=False)

    class Meta:
        model = TripdetailInfo
        fields = ['tr_updated_by','tr_enquirynumber','tr_consignmentnumber','tr_tripnumber','tr_vehicletype','tr_vehiclesource','tr_vehiclenumber','tr_vehicletype_placed','tr_category','tr_departedlocation','tr_reportedlocation','tc_tripcost','tc_parkingcost','tc_tollcost','tc_loadingcost','tc_unloadingcost','tc_weighmentcost','tc_handlingcost','tc_handlingcost_reason','tr_iou','tc_financestatus','tr_customerref','tc_no_of_days_halting','tc_supervisorcost','tc_haltingcost','tc_total_halting_cost','tc_rtocost','tc_betacost','tc_cancellation','tc_tripcost_check','tc_parkingcost_check','tc_tollcost_check','tc_loadingcost_check','tc_unloadingcost_check','tc_weighmentcost_check','tc_supervisorcost_check','tc_handlingcost_check','tc_haltingcost_check','tc_total_halting_cost_check','tc_rtocost_check','tc_betacost_check','tc_cancellation_check','tc_tripcost_vendor_check','tc_parkingcost_vendor_check','tc_tollcost_vendor_check','tc_loadingcost_vendor_check','tc_unloadingcost_vendor_check','tc_weighmentcost_vendor_check','tc_supervisorcost_vendor_check','tc_handlingcost_vendor_check','tc_haltingcost_vendor_check','tc_total_halting_cost_vendor_check','tc_rtocost_vendor_check','tc_betacost_vendor_check','tc_cancellation_vendor_check']
    def __init__(self, *args, **kwargs):
        super(TripclosureaddForm,self).__init__(*args, **kwargs)
        self.fields['tr_enquirynumber'].empty_label = "--Select--"
        self.fields['tr_consignmentnumber'].empty_label = "--Select--"
        self.fields['tc_financestatus'].empty_label = "--Select--"
        self.fields['tr_iou'].empty_label = "--Select--"
        
        # Optimize ForeignKey querysets so Django does not load thousands of records during field rendering
        inst = kwargs.get('instance')
        if inst:
            if hasattr(inst, 'tr_enquirynumber_id') and inst.tr_enquirynumber_id:
                from ..models import EnquirynoteInfo
                self.fields['tr_enquirynumber'].queryset = EnquirynoteInfo.objects.filter(pk=inst.tr_enquirynumber_id)
            if hasattr(inst, 'tr_consignmentnumber_id') and inst.tr_consignmentnumber_id:
                from ..models import ConsignmentdetailInfo
                self.fields['tr_consignmentnumber'].queryset = ConsignmentdetailInfo.objects.filter(pk=inst.tr_consignmentnumber_id)
            if hasattr(inst, 'tr_vehiclenumber_id') and inst.tr_vehiclenumber_id:
                from ..models import VehiclemasterInfo
                self.fields['tr_vehiclenumber'].queryset = VehiclemasterInfo.objects.filter(pk=inst.tr_vehiclenumber_id)

        # Default "Trip Charges" checkboxes to True
        if 'tc_tripcost_check' in self.fields:
            self.fields['tc_tripcost_check'].initial = True
        if 'tc_tripcost_vendor_check' in self.fields:
            self.fields['tc_tripcost_vendor_check'].initial = True

class TripclosurefilesForm(forms.ModelForm):
    class Meta:
        model = Trip_closure_files_Info
        fields = '__all__'
        widgets = {
            'tcf_trip_cost': forms.FileInput(),
            'tcf_parking_cost': forms.FileInput(),
            'tcf_toll_cost': forms.FileInput(),
            'tcf_loading_cost': forms.FileInput(),
            'tcf_unloading_cost': forms.FileInput(),
            'tcf_weighment_cost': forms.FileInput(),
            'tcf_handling_cost': forms.FileInput(),
            'tcf_pod': forms.FileInput(),
        }