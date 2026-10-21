from django import forms
from django.db.models import Q
from ..models import Vehicle_allotmentInfo, VehiclemasterInfo, TripdetailInfo

class VehicleallotmentForm(forms.ModelForm):
    va_vehicletype_selection_requested = forms.BooleanField(initial=True,required=False)
    va_vehicletype_selection_placed = forms.BooleanField(required=False)
    class Meta:
        model = Vehicle_allotmentInfo
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(VehicleallotmentForm,self).__init__(*args, **kwargs)
        if 'va_vehiclesource' in self.fields:
            self.fields['va_vehiclesource'].empty_label = "--Select--"
        if 'va_vehicletype_placed' in self.fields:
            self.fields['va_vehicletype_placed'].empty_label = "--Select--"
        if 'va_vehicletype' in self.fields:
            self.fields['va_vehicletype'].empty_label = "--Select--"
        if 'va_vehiclenumber' in self.fields:
            self.fields['va_vehiclenumber'].empty_label = "--Select--"
            curr_id = self.instance.va_vehiclenumber_id if self.instance else None

            closed_status_ids = [2, 3, 4, 5, 7, 9, 10, 11]
            open_trip_regs = set(
                t.strip().upper() for t in TripdetailInfo.objects.filter(
                    Q(tc_financestatus_id=1) |
                    Q(tr_operational_status_id__in=[1, 12]) |
                    (~Q(tc_financestatus_id__in=closed_status_ids) & ~Q(tr_operational_status_id__in=closed_status_ids))
                ).exclude(
                    tr_enquirynumber__en_status_id=8
                ).values_list('tr_vehiclenumber', flat=True) if t
            )

            busy_vehicle_ids = set(VehiclemasterInfo.objects.filter(
                vm_registrationnumber__in=list(open_trip_regs)
            ).values_list('id', flat=True)) if open_trip_regs else set()

            busy_allotments_qs = Vehicle_allotmentInfo.objects.filter(
                Q(va_created_at__date__gte='2026-08-01') | Q(va_enquirynumber__en_created_at__date__gte='2026-08-01')
            ).exclude(
                va_status_id__in=[2, 3, 4, 5]
            ).exclude(
                va_enquirynumber__en_status_id=8
            ).exclude(va_vehiclenumber__isnull=True).select_related('va_vehiclenumber')

            allotments = list(busy_allotments_qs)
            enquiry_ids = [a.va_enquirynumber_id for a in allotments]
            vehicle_regs = [a.va_vehiclenumber.vm_registrationnumber for a in allotments if a.va_vehiclenumber]

            trips_qs = TripdetailInfo.objects.filter(
                tr_enquirynumber_id__in=enquiry_ids,
                tr_vehiclenumber__in=vehicle_regs
            ).values('tr_enquirynumber_id', 'tr_vehiclenumber', 'tr_operational_status_id', 'tc_financestatus_id')

            trip_map = {}
            for t in trips_qs:
                key = (t['tr_enquirynumber_id'], (t['tr_vehiclenumber'] or '').strip().upper())
                if key not in trip_map:
                    trip_map[key] = []
                op_status = t['tr_operational_status_id'] if t['tr_operational_status_id'] else 1
                fin_status = t['tc_financestatus_id'] if t['tc_financestatus_id'] else 1
                trip_map[key].append((op_status, fin_status))

            for a in allotments:
                if not a.va_vehiclenumber:
                    continue
                key = (a.va_enquirynumber_id, (a.va_vehiclenumber.vm_registrationnumber or '').strip().upper())
                if key in trip_map:
                    has_active_trip = any(
                        (op in [1, 12] or fin == 1 or (op not in closed_status_ids and fin not in closed_status_ids))
                        for op, fin in trip_map[key]
                    )
                    if has_active_trip:
                        busy_vehicle_ids.add(a.va_vehiclenumber_id)
                else:
                    # Vehicle is in 'Vehicle Assigned' status with no trip created yet
                    busy_vehicle_ids.add(a.va_vehiclenumber_id)

            if curr_id:
                busy_vehicle_ids.discard(curr_id)
                self.fields['va_vehiclenumber'].queryset = VehiclemasterInfo.objects.filter(
                    (Q(vm_status_id=1) | Q(vm_status__isnull=True) | Q(pk=curr_id))
                ).exclude(id__in=busy_vehicle_ids)
            else:
                self.fields['va_vehiclenumber'].queryset = VehiclemasterInfo.objects.filter(
                    Q(vm_status_id=1) | Q(vm_status__isnull=True)
                ).exclude(id__in=busy_vehicle_ids)
        if 'va_vendor' in self.fields:
            self.fields['va_vendor'].empty_label = "--Select--"
        if 'va_status' in self.fields:
            self.fields['va_status'].empty_label = "--Select--"
        if 'va_updated_by' in self.fields:
            self.fields['va_updated_by'].required = False
        if 'va_created_by' in self.fields:
            self.fields['va_created_by'].required = False
        if 'va_enquirynumber' in self.fields:
            self.fields['va_enquirynumber'].required = False
        if 'va_driver_lic_expiry' in self.fields:
            self.fields['va_driver_lic_expiry'].widget.attrs['readonly'] = 'readonly'
            self.fields['va_driver_lic_expiry'].widget.attrs['style'] = 'pointer-events: none;'

    #  BUSINESS RULE VALIDATION
    def clean(self):
        cleaned_data = super().clean()

        vehicle_source = cleaned_data.get("va_vehiclesource")
        driver_name = cleaned_data.get("va_drivername")

        # OWN (1) or ATTACHED (2) - only check driver_name since driver_id is not a form field
        if vehicle_source and vehicle_source.id in [1, 2]:
            if not driver_name:
                self.add_error('va_drivername', "Driver Name is required for OWN and ATTACHED vehicles.")
            if not cleaned_data.get("va_vehiclenumber"):
                self.add_error('va_vehiclenumber', "Vehicle Number is required for OWN and ATTACHED vehicles.")

        # MARKET (3) - check vendor
        if vehicle_source and vehicle_source.id == 3:
            if not cleaned_data.get("va_vendor"):
                self.add_error('va_vendor', "Vendor Name is required for MARKET vehicles.")

        return cleaned_data
