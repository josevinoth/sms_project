from django import forms
from ..sub_models.attached_bill_mod import AttachedBillInfo
from ..sub_models.vendor_info_mod import Vendor_info
from ..sub_models.vehiclemaster_mod import VehiclemasterInfo

class AttachedBillForm(forms.ModelForm):
    class Meta:
        model = AttachedBillInfo
        fields = [
            'ab_vendor', 'ab_vehicle_number', 'ab_vehicle_type', 'ab_bill_no',
            'ab_bill_date', 'ab_from_date', 'ab_to_date', 'ab_buy_cost', 'ab_toll_cost',
            'ab_leave_days', 'ab_leave_amount',
            'ab_agreed_km', 'ab_total_km_run', 'ab_extra_km_run',
            'ab_extra_km_amount', 'ab_bill_amount', 'ab_bill_upload', 'ab_selected_trips'
        ]
        # Add TDS related fields similar to MarketBill; include TDS type before percent
        fields[ fields.index('ab_bill_amount')+1:fields.index('ab_bill_upload') ] = ['ab_tds_type', 'ab_tds_percent', 'ab_tds_amount', 'ab_payable_amount']

    def __init__(self, *args, **kwargs):
        super(AttachedBillForm, self).__init__(*args, **kwargs)
        
        # 1. Filter Vendor dropdown to show only "Attached" vendors
        # An attached vendor is one who has vehicles with ownership_id=2 (Attached)
        self.fields['ab_vendor'].queryset = Vendor_info.objects.filter(
            vehiclemasterinfo__vm_ownership_id=2
        ).distinct().order_by('vend_name')

        # Adding form-control class to all fields and setting common attributes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
            # Date widgets
            if field_name in ['ab_bill_date', 'ab_from_date', 'ab_to_date']:
                field.widget = forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})

            if field_name == 'ab_tds_type':
                # Render TDS type as a select with placeholder
                field.widget = forms.Select(choices=[('', 'Select'), ('Company', 'Company'), ('Non company', 'Non company')], attrs={'class': 'form-control', 'id': 'id_ab_tds_type'})
            
            if field_name == 'ab_selected_trips':
                field.widget = forms.HiddenInput()
            
            # Read-only fields (Calculated/Pulled)
            if field_name in ['ab_vehicle_type', 'ab_total_km_run', 'ab_leave_amount', 'ab_extra_km_run', 'ab_tds_amount', 'ab_payable_amount']:
                field.widget.attrs['readonly'] = 'readonly'
            
            # Empty labels
            if hasattr(field, 'empty_label'):
                field.empty_label = "--Select--"

        # 2. Dependent Queryset for Vehicle Number (Filtered for Attached ownership_id=2)
        if 'ab_vendor' in self.data:
            try:
                vendor_id = int(self.data.get('ab_vendor'))
                self.fields['ab_vehicle_number'].queryset = VehiclemasterInfo.objects.filter(
                    vm_vendor_id=vendor_id, vm_ownership_id=2
                ).order_by('vm_registrationnumber')
            except (ValueError, TypeError):
                self.fields['ab_vehicle_number'].queryset = VehiclemasterInfo.objects.none()
        elif self.instance.pk:
            self.fields['ab_vehicle_number'].queryset = VehiclemasterInfo.objects.filter(
                vm_vendor=self.instance.ab_vendor, vm_ownership_id=2
            ).order_by('vm_registrationnumber')
        else:
             # Initially empty or filtered by ownership for attached vehicles
             self.fields['ab_vehicle_number'].queryset = VehiclemasterInfo.objects.filter(
                 vm_ownership_id=2
             ).order_by('vm_registrationnumber')
