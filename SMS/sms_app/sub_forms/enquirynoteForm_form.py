from django import forms
from ..models import EnquirynoteInfo

class EnquirynoteaddForm(forms.ModelForm):

    class Meta:
        model = EnquirynoteInfo
        exclude = (
            'en_agent_name', 'en_sub_customer', 'en_plant_code',
            'en_is_approved', 'en_approved_by', 'en_approved_date',
            'en_requested_arrival_time', 'en_requested_delivery_time', 'en_otd_cutoff',
            'en_buyer_name', 'en_po_numbers', 'en_shipment_type',
            'en_vessel_name', 'en_voyage_no', 'en_bl_cutoff', 'en_special_instructions',
            'en_vehicle_req_time', 'en_no_of_vehicles', 'en_no_of_pcs',
            'en_weight', 'en_dimensions', 'en_cbm',
            'en_pickup_contact_name', 'en_pickup_contact_mobile',
            'en_delivery_contact_name', 'en_delivery_contact_mobile',
        )

    def __init__(self, *args, **kwargs):
        super(EnquirynoteaddForm,self).__init__(*args, **kwargs)
        self.fields['en_customername'].empty_label = "--Select--"
        self.fields['en_customername'].queryset = self.fields['en_customername'].queryset.filter(cu_name__icontains='(T)')
        self.fields['en_customerdepartment'].empty_label = "--Select--"
        self.fields['en_assignedto'].empty_label = "--Select--"
        self.fields['en_status'].empty_label = "--Select--"
        self.fields['en_fromlocaion'].empty_label = "--Select--"
        self.fields['en_tolocation'].empty_label = "--Select--"
        self.fields['en_touchpoint'].empty_label = "--Select--"
        self.fields['en_touchpoint2'].empty_label = "--Select--"
        self.fields['en_touchpoint3'].empty_label = "--Select--"
        self.fields['en_touchpoint4'].empty_label = "--Select--"
        self.fields['en_business_type'].empty_label = "--Select--"
        self.fields['en_movement_type'].empty_label = "--Select--"
        self.fields['en_trip_type'].empty_label = "--Select--"
        self.fields['en_trip_type'].required = True