from django import forms
from ..models import PackingGateReturn, PkcostingsummaryInfo, PkToolMaster

class GatepassreturnForm(forms.ModelForm):
    gp_job_no = forms.ChoiceField(
        choices=[('', '--Select--')], 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'gp_job_no'})
    )

    class Meta:
        model = PackingGateReturn
        fields = '__all__'
        widgets = {
            'gp_consignment_note_no': forms.TextInput(attrs={'class': 'form-control'}),
            'gp_consignment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gp_hsn_code': forms.TextInput(attrs={'class': 'form-control'}),
            'gp_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'gp_tools': forms.SelectMultiple(attrs={'class': 'form-control select2', 'multiple': 'multiple'}),
            
            # New DC widgets
            'gp_customer_ship_to_gstin': forms.TextInput(attrs={'class': 'form-control'}),
            'gp_customer_bill_to_gstin': forms.TextInput(attrs={'class': 'form-control'}),
            'gp_grn_ref': forms.TextInput(attrs={'class': 'form-control'}),
            'gp_stock_register_ref': forms.TextInput(attrs={'class': 'form-control'}),
            'gp_sales_order_ref': forms.TextInput(attrs={'class': 'form-control'}),
            'gp_returnable_status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'gp_consignment_date': 'Gate Pass Date',
            'gp_tools': 'Select Tools (For On-Site)',
        }

    def __init__(self, *args, **kwargs):
        super(GatepassreturnForm,self).__init__(*args, **kwargs)
        
        # Customize tool dropdown display: Tool Name - Serial Number
        # Using list() to force evaluation and prevent cursor issues on some DB environments
        available_tools = list(PkToolMaster.objects.filter(tm_status='Available').only('tm_name', 'tm_serial_no', 'id'))
        self.fields['gp_tools'].queryset = PkToolMaster.objects.filter(id__in=[t.id for t in available_tools])
        self.fields['gp_tools'].label_from_instance = lambda obj: f"{obj.tm_name} - {obj.tm_serial_no}"
        
        import datetime
        if not self.instance.pk and not self.initial.get('gp_consignment_date'):
            self.initial['gp_consignment_date'] = datetime.date.today()
        
        self.fields['gp_customer_name'].empty_label = "--Select--"
        self.fields['gp_assessment_num'].empty_label = "--Select--"
        self.fields['gp_customer_po'].empty_label = "--Select--"
        self.fields['gp_packing_location'].empty_label = "--Select--"
        self.fields['gp_transporter_name'].empty_label = "--Select--"
        self.fields['gp_veh_type'].empty_label = "--Select--"
        
        # Initial choices
        choices = [('', '--Select--')]
        
        # Determine which customer to get jobs for
        # During POST, use the submitted customer. During GET, use the instance.
        customer_id = None
        if 'gp_customer_name' in self.data:
            try:
                customer_id = int(self.data.get('gp_customer_name'))
            except (ValueError, TypeError):
                pass
        elif self.instance and self.instance.pk and self.instance.gp_customer_name:
            customer_id = self.instance.gp_customer_name.id
        elif self.initial.get('gp_customer_name'):
            cust = self.initial.get('gp_customer_name')
            customer_id = cust.id if hasattr(cust, 'id') else cust
        
        # If we have a saved job numbering in the instance (for display)
        if self.instance and self.instance.gp_job_no:
            if (self.instance.gp_job_no, self.instance.gp_job_no) not in choices:
                choices.append((self.instance.gp_job_no, self.instance.gp_job_no))
        
        # Also ensure the submitted or initial job_no is in choices so validation passes
        if 'gp_job_no' in self.data:
            submitted_job = self.data.get('gp_job_no')
            if submitted_job and (submitted_job, submitted_job) not in choices:
                choices.append((submitted_job, submitted_job))
        elif self.initial.get('gp_job_no'):
            initial_job = self.initial.get('gp_job_no')
            if initial_job and (initial_job, initial_job) not in choices:
                choices.append((initial_job, initial_job))

        # Add other jobs for the selected customer — only if production is COMPLETED
        if customer_id:
            from ..sub_models.packing_jobs_mod import Packingjobs

            # Only allow jobs that have passed the Quality Check
            approved_job_nos = Packingjobs.objects.filter(
                pj_production_completed_flag='Completed',
                pj_qc_completed_flag='Completed'
            ).values_list('pj_job_no', flat=True)

            # Get Job Numbers that ALREADY have a Gate Pass (exclude current instance)
            existing_jobs = PackingGateReturn.objects.exclude(
                pk=self.instance.pk if self.instance.pk else None
            ).values_list('gp_job_no', flat=True)

            job_no_qs = PkcostingsummaryInfo.objects.filter(
                cs_customer_name=customer_id,
                cs_job_no__isnull=False,
                cs_job_no__in=approved_job_nos,
            ).exclude(
                cs_job_no__in=existing_jobs
            ).exclude(cs_job_no='').values_list('cs_job_no', flat=True).distinct()
            
            for job in job_no_qs:
                if job and (job, job) not in choices:
                    choices.append((job, job))
                
        self.fields['gp_job_no'].choices = choices

