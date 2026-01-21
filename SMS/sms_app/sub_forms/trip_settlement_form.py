from django import forms
from ..models import TripdetailInfo, Tripstatusinfo,Trip_closure_files_Info


class TripSettlementForm(forms.ModelForm):
    class Meta:
        model = TripdetailInfo
        fields = ['tr_updated_by', 'tr_enquirynumber', 'tr_consignmentnumber', 'tr_tripnumber', 'tr_vehicletype',
                  'tr_vehiclesource', 'tr_vehiclenumber', 'tr_vehicletype_placed', 'tr_category', 'tr_departedlocation',
                  'tr_reportedlocation', 'tc_tripcost', 'tc_parkingcost', 'tc_tollcost', 'tc_loadingcost',
                  'tc_unloadingcost', 'tc_weighmentcost', 'tc_handlingcost', 'tr_iou', 'tc_financestatus',
                  'tr_customerref', 'tc_no_of_days_halting', 'tc_supervisorcost', 'tc_haltingcost','tc_rtocost', 'tc_betacost']


    def __init__(self, *args, **kwargs):
        super(TripSettlementForm, self).__init__(*args, **kwargs)
        self.fields['tr_enquirynumber'].empty_label = "--Select--"
        self.fields['tr_consignmentnumber'].empty_label = "--Select--"
        self.fields['tc_financestatus'].empty_label = "--Select--"
        self.fields['tr_iou'].empty_label = "--Select--"
        # Only show Trip Settled & Clarification
        self.fields['tc_financestatus'].queryset = Tripstatusinfo.objects.filter(
            id__in=[7, 4]   # Trip Settled, Clarification
        )

        self.fields['tc_financestatus'].label = "Settlement Status"

class TripclosurefilesForm(forms.ModelForm):
    class Meta:
        model = Trip_closure_files_Info
        fields = '__all__'
        # fields=('dam_OTL_pic','dam_document')