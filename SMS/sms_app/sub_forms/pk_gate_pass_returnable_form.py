from django import forms
from ..models import PackingGateReturn, PkcostingsummaryInfo

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
        }
        labels = {
            'gp_consignment_date': 'Gate Pass Date',
        }

    def __init__(self, *args, **kwargs):
        super(GatepassreturnForm,self).__init__(*args, **kwargs)
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
        
        # If we have a saved job numbering in the instance (for display)
        if self.instance and self.instance.gp_job_no:
            if (self.instance.gp_job_no, self.instance.gp_job_no) not in choices:
                choices.append((self.instance.gp_job_no, self.instance.gp_job_no))
        
        # Also ensure the submitted job_no is in choices so validation passes
        if 'gp_job_no' in self.data:
            submitted_job = self.data.get('gp_job_no')
            if submitted_job and (submitted_job, submitted_job) not in choices:
                choices.append((submitted_job, submitted_job))

        # Add other jobs for the selected customer to keep the dropdown full
        if customer_id:
            # Get Job Numbers that ALREADY have a Gate Pass
            # We exclude the current instance's job so it remains visible when editing
            existing_jobs = PackingGateReturn.objects.exclude(
                pk=self.instance.pk if self.instance.pk else None
            ).values_list('gp_job_no', flat=True)

            job_no_qs = PkcostingsummaryInfo.objects.filter(
                cs_customer_name=customer_id,
                cs_job_no__isnull=False
            ).exclude(
                cs_job_no__in=existing_jobs
            ).exclude(cs_job_no='').values_list('cs_job_no', flat=True).distinct()
            
            for job in job_no_qs:
                if job and (job, job) not in choices:
                    choices.append((job, job))
                
        self.fields['gp_job_no'].choices = choices
