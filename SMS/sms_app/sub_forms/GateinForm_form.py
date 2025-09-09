from django import forms
from django.db.models import Q
from django.utils.timezone import now
from datetime import timedelta

from ..models import Gatein_info,Gatein_pre_info,Pregateintruckinfo



class GateinaddForm(forms.ModelForm):
    class Meta:
        model = Gatein_info
        fields = '__all__'
        # fields = ['gatein_job_no','gatein_invoice','gatein_customer','gatein_customer_type','gatein_arrival_date','gatein_department','gatein_shipper','gatein_consignee','gatein_no_of_pkg','gatein_weight','gatein_driver','gatein_contact_number','gatein_DL_number','gatein_otl','gatein_transporter','gatein_truck_number','gatein_truck_type','gatein_status','gatein_pre_id','gatein_updated_by']

    def __init__(self, *args, **kwargs):
        super(GateinaddForm, self).__init__(*args, **kwargs)
        self.fields['gatein_driver'].empty_label = "--Select--"
        self.fields['gatein_status'].empty_label = "--Select--"
        self.fields['gatein_customer'].empty_label = "--Select--"
        self.fields['gatein_department'].empty_label = "--Select--"
        self.fields['gatein_customer_type'].empty_label = "--Select--"
        self.fields['gatein_pre_id'].empty_label = "--Select--"
        three_days_ago = now() - timedelta(days=3)
        Gatein_pre_info.objects.filter(
            gatein_pre_created_at__lte=three_days_ago,
            gatein_pre_status__id__lt=5  # Only update if not already completed
        ).update(gatein_pre_status_id=5)
        current_pre_id = self.instance.gatein_pre_id_id if self.instance.pk else None
        self.fields['gatein_pre_id'].queryset = Gatein_pre_info.objects.filter(Q(gatein_pre_created_at__gte=three_days_ago) | Q(pk=current_pre_id))
        self.fields['gatein_updated_by'].empty_label = "--Select--"
        self.fields['gatein_comodity'].empty_label = "--Select--"
        self.fields['gatein_cargo'].empty_label = "--Select--"
        # self.fields['gatein_pre_id'].queryset = Gatein_pre_info.objects.order_by('-id')[:50]
        self.fields['gatein_pre_id'].widget.attrs.update({
            'class': 'form-control select2',  # Add Select2 class
            'data-placeholder': 'Search for Gatein Pre-Info...',
            'style': 'width: 100%',
        })
