from django import forms
from ..sub_models.maintenance_bill_mod import MaintenanceBillInfo
from ..sub_models.maintenance_mod import MaintenanceInfo

class MaintenanceBillForm(forms.ModelForm):
    mnb_maintenance = forms.ModelChoiceField(
        queryset=MaintenanceInfo.objects.filter(mi_approval_status_id=3),
        empty_label="-- Select Vehicle No --",
        label="Vehicle No"
    )

    class Meta:
        model = MaintenanceBillInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(MaintenanceBillForm, self).__init__(*args, **kwargs)
        
        # Filter to only unbilled maintenance records with Finance Approved status (3)
        unbilled_q = MaintenanceInfo.objects.filter(
            mi_approval_status_id=3,
            bills_v1__isnull=True
        )
        
        # In Edit mode, allow the already selected maintenance record to stay in the queryset
        if self.instance and self.instance.pk and self.instance.mnb_maintenance:
            from django.db.models import Q
            self.fields['mnb_maintenance'].queryset = MaintenanceInfo.objects.filter(
                Q(id=self.instance.mnb_maintenance.id) | Q(id__in=unbilled_q.values_list('id', flat=True))
            )
        else:
            self.fields['mnb_maintenance'].queryset = unbilled_q

        # Customizing the display labels for mnb_maintenance dropdown - only Vehicle No
        self.fields['mnb_maintenance'].label_from_instance = lambda obj: f"{obj.mi_vehicle.vm_registrationnumber}"
        
        # Adding form-control class to all fields and setting common attributes
        for field_name, field in self.fields.items():
            existing_class = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'form-control {existing_class}'.strip()
            
            if field_name == 'mnb_bill_date':
                field.widget = forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
            elif field_name == 'mnb_remarks':
                field.widget.attrs['rows'] = 1
            elif field_name == 'mnb_bill_upload':
                field.widget = forms.FileInput(attrs={'class': 'form-control'})
            elif field_name in ['mnb_gst_amount', 'mnb_total_amount', 'mnb_tds_amount', 'mnb_amount_payable']:
                field.widget.attrs['readonly'] = 'readonly'
            
            # Setting empty labels for all choice fields
            if isinstance(field, forms.ModelChoiceField) or isinstance(field, forms.ChoiceField):
                field.empty_label = "--Select--"
        
        # Explicitly set the expenses type choices if needed, but it should be in the model
        self.fields['mnb_expenses_type'].choices = [('Vehicle Maintenance', 'Vehicle Maintenance')]
