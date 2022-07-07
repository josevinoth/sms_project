from django import forms
from ..models import Loadingbay_Info

class LoadingbayddForm(forms.ModelForm):
    class Meta:
        model = Loadingbay_Info
        # fields = ['lb_job_no','lb_invoice']
        fields = '__all__'

        def __init__(self, *args, **kwargs):
            super(LoadingbayddForm, self).__init__(*args, **kwargs)
            self.fields['lb_otl_check'].empty_label = "--Select--"
            self.fields['lb_offload_acceptance'].empty_label = "--Select--"
            self.fields['lb_offload_acceptance'].queryset = self.fields['lb_offload_acceptance'].queryset.order_by('name')
            # self.fields['wh_stock_invoice_currency'].empty_label = "--Select--"