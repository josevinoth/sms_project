from django import forms
from ..models import Gatein_info



class GateinaddmblForm(forms.ModelForm):
    class Meta:
        model = Gatein_info

        fields = ['gatein_updated_by','gatein_job_status','gatein_driver','gatein_status','gatein_customer','gatein_department',
                  'gatein_customer_type','gatein_pre_id','gatein_comodity','gatein_cargo']

    def __init__(self, *args, **kwargs):
        super(GateinaddmblForm, self).__init__(*args, **kwargs)
        self.fields['gatein_driver'].empty_label = "--Select--"
        self.fields['gatein_status'].empty_label = "--Select--"
        self.fields['gatein_customer'].empty_label = "--Select--"
        self.fields['gatein_department'].empty_label = "--Select--"
        self.fields['gatein_customer_type'].empty_label = "--Select--"
        self.fields['gatein_pre_id'].empty_label = "--Select--"
        self.fields['gatein_updated_by'].empty_label = "--Select--"
        self.fields['gatein_job_status'].empty_label = "--Select--"
        self.fields['gatein_comodity'].empty_label = "--Select--"
        self.fields['gatein_cargo'].empty_label = "--Select--"
        # self.fields['gatein_pre_id'].queryset = Gatein_pre_info.objects.order_by('-id')[:50]
        self.fields['gatein_pre_id'].widget.attrs.update({
            'class': 'form-control select2',  # Add Select2 class
            'data-placeholder': 'Search for Gatein Pre-Info...',
            'style': 'width: 100%',
        })
