from django import forms
from ..models import SaleEnquiry

class SaleEnquiryForm(forms.ModelForm):
    sales_number = forms.ChoiceField(
        choices=[('', '---------')], 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'sales_number_input'})
    )
    
    class Meta:
        model = SaleEnquiry
        fields = [
            'enquiry_id', 'enquiry_date_time', 'enquiry_source', 'branch', 'customer_name',
            'new_customer_name', 'customer_code', 'contact_person_name', 'contact_no', 'mail',
            'address', 'remarks', 'service_type', 'sales_number',
            'wh_customer_type', 'wh_sqft_req', 'wh_scope_of_lul',
            'wh_tonnage', 'wh_no_of_months_req', 'wh_rfq_closed_date', 'wh_remarks',
            'tr_customer_type', 'tr_no_of_vehicles_req', 'tr_veh_type_req',
            'tr_from', 'tr_to', 'tr_rfq_closed_date', 'tr_remarks', 'tr_no_of_avg_trips_per_month', 'tr_tonnage',
            'pa_customer_type', 'pa_inhouse_onsite', 'pa_lul_scope', 'pa_transport_scope', 'pa_no_of_boxes_per_month', 'pa_rfq_closed_date', 'pa_remarks',
            'ex_customer_type', 'ex_veh_type', 'ex_no_of_vehicles', 'ex_pickup', 'ex_delivery', 'ex_shipment_type', 'ex_no_of_shipments', 'ex_avg_weight_per_shipment', 'ex_delivery_type', 'ex_rfq_closed_date', 'ex_remarks',
            'su_customer_type', 'su_no_of_manpowers', 'su_shift_type', 'su_working_days', 'su_supervisors', 'su_loaders', 'su_rfq_closed_date', 'su_remarks',
            'mc_customer_type', 'mc_tour_type', 'mc_travel_type', 'mc_mode_of_transport', 'mc_from', 'mc_to', 'mc_no_of_passengers', 'mc_travel_date', 'mc_return_date', 'mc_vehicle_source', 'mc_vehicle_type', 'mc_package_req', 'mc_hotel_req', 'mc_rfq_closed_date', 'mc_remarks',
            'wh_attachment', 'tr_attachment', 'pa_attachment', 'ex_attachment', 'su_attachment', 'mc_attachment'
        ]
        widgets = {
            'enquiry_id': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'enquiry_date_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'enquiry_source': forms.Select(attrs={'class': 'form-control select2'}),
            'branch': forms.Select(attrs={'class': 'form-control select2'}),
            'customer_name': forms.Select(attrs={'class': 'form-control select2', 'id': 'customer_name_select'}),
            'new_customer_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'new_customer_name_input', 'placeholder': 'Enter if new customer'}),
            'customer_code': forms.TextInput(attrs={'class': 'form-control', 'id': 'customer_code_input'}),
            'contact_person_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_no': forms.TextInput(attrs={'class': 'form-control'}),
            'mail': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'service_type': forms.TextInput(attrs={'class': 'form-control'}),
            'wh_customer_type': forms.Select(attrs={'class': 'form-control select2', 'id': 'wh_customer_type_select'}),
            'wh_sqft_req': forms.NumberInput(attrs={'class': 'form-control'}),
            'wh_scope_of_lul': forms.TextInput(attrs={'class': 'form-control'}),
            'wh_tonnage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'wh_no_of_months_req': forms.NumberInput(attrs={'class': 'form-control'}),
            'wh_rfq_closed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'wh_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'tr_customer_type': forms.Select(attrs={'class': 'form-control select2', 'id': 'tr_customer_type_select'}),
            'tr_no_of_vehicles_req': forms.NumberInput(attrs={'class': 'form-control'}),
            'tr_veh_type_req': forms.TextInput(attrs={'class': 'form-control'}),
            'tr_from': forms.TextInput(attrs={'class': 'form-control'}),
            'tr_to': forms.TextInput(attrs={'class': 'form-control'}),
            'tr_rfq_closed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tr_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'tr_no_of_avg_trips_per_month': forms.NumberInput(attrs={'class': 'form-control'}),
            'tr_tonnage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pa_customer_type': forms.Select(attrs={'class': 'form-control select2', 'id': 'pa_customer_type_select'}),
            'pa_inhouse_onsite': forms.TextInput(attrs={'class': 'form-control'}),
            'ex_customer_type': forms.Select(attrs={'class': 'form-control select2', 'id': 'ex_customer_type_select'}),
            'pa_lul_scope': forms.TextInput(attrs={'class': 'form-control'}),
            'pa_transport_scope': forms.TextInput(attrs={'class': 'form-control'}),
            'pa_no_of_boxes_per_month': forms.NumberInput(attrs={'class': 'form-control'}),
            'pa_rfq_closed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pa_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'ex_veh_type': forms.TextInput(attrs={'class': 'form-control'}),
            'ex_no_of_vehicles': forms.NumberInput(attrs={'class': 'form-control'}),
            'ex_pickup': forms.TextInput(attrs={'class': 'form-control'}),
            'ex_delivery': forms.TextInput(attrs={'class': 'form-control'}),
            'ex_shipment_type': forms.Select(attrs={'class': 'form-control select2', 'id': 'ex_shipment_type_select'}),
            'ex_no_of_shipments': forms.NumberInput(attrs={'class': 'form-control'}),
            'ex_avg_weight_per_shipment': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ex_delivery_type': forms.Select(attrs={'class': 'form-control select2', 'id': 'ex_delivery_type_select'}),
            'ex_rfq_closed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ex_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'su_customer_type': forms.Select(attrs={'class': 'form-control select2', 'id': 'su_customer_type_select'}),
            'su_no_of_manpowers': forms.NumberInput(attrs={'class': 'form-control'}),
            'su_shift_type': forms.TextInput(attrs={'class': 'form-control'}),
            'su_working_days': forms.TextInput(attrs={'class': 'form-control'}),
            'su_supervisors': forms.NumberInput(attrs={'class': 'form-control'}),
            'su_loaders': forms.NumberInput(attrs={'class': 'form-control'}),
            'su_rfq_closed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'su_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'mc_customer_type': forms.Select(attrs={'class': 'form-control select2', 'id': 'mc_customer_type_select'}),
            'mc_tour_type': forms.Select(attrs={'class': 'form-control select2', 'id': 'mc_tour_type_select'}),
            'mc_travel_type': forms.Select(attrs={'class': 'form-control select2', 'id': 'mc_travel_type_select'}),
            'mc_mode_of_transport': forms.Select(attrs={'class': 'form-control select2', 'id': 'mc_mode_of_transport_select'}),
            'mc_from': forms.TextInput(attrs={'class': 'form-control'}),
            'mc_to': forms.TextInput(attrs={'class': 'form-control'}),
            'mc_no_of_passengers': forms.NumberInput(attrs={'class': 'form-control'}),
            'mc_travel_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'mc_return_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'mc_vehicle_source': forms.Select(attrs={'class': 'form-control select2', 'id': 'mc_vehicle_source_select'}),
            'mc_vehicle_type': forms.TextInput(attrs={'class': 'form-control'}),
            'mc_package_req': forms.TextInput(attrs={'class': 'form-control'}),
            'mc_hotel_req': forms.TextInput(attrs={'class': 'form-control'}),
            'mc_rfq_closed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'mc_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'sales_number': forms.Select(attrs={'class': 'form-control select2', 'id': 'sales_number_input'}),
        }

    def __init__(self, *args, **kwargs):
        super(SaleEnquiryForm, self).__init__(*args, **kwargs)
        from ..models import SalesInfo
        # Fetch all sales records to populate the dropdown
        sales_records = SalesInfo.objects.all().order_by('-s_created_at')
        sales_choices = [('', '---------')]
        for record in sales_records:
            if not record.s_sale_number:
                continue
            trimmed_sale_number = record.s_sale_number.replace('26-27_', '')
            if record.s_customer_new_name:
                label = f"{trimmed_sale_number} ({record.s_customer_new_name})"
            elif record.s_customer_name:
                label = f"{trimmed_sale_number} ({record.s_customer_name})"
            else:
                label = trimmed_sale_number
            sales_choices.append((record.s_sale_number, label))

        self.fields['sales_number'].choices = sales_choices
        if self.instance and self.instance.pk:
            self.fields['sales_number'].initial = self.instance.sales_number
        self.fields['mc_vehicle_source'].empty_label = "--Select--"
