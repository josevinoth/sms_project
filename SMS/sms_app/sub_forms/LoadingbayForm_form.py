from django import forms
from django.forms import HiddenInput

from ..models import Loadingbay_Info,Loadingbayimages_Info

class LoadingbayddForm(forms.ModelForm):
    class Meta:
        model = Loadingbay_Info
        # fields = ['lb_job_no','lb_invoice']
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(LoadingbayddForm, self).__init__(*args, **kwargs)
        self.fields['lb_otl_check'].empty_label = "--Select--"
        self.fields['lb_offload_acceptance'].empty_label = "--Select--"
        self.fields['lb_otl_check'].empty_label = "--Select--"
        self.fields['lb_offload_acceptance'].empty_label = "--Select--"
        self.fields['lb_stock_invoice_currency'].empty_label = "--Select--"
        self.fields['lb_stock_type'].empty_label = "--Select--"
        self.fields['lb_packing_list'].empty_label = "--Select--"
        self.fields['lb_status'].empty_label = "--Select--"


class LoadingbayImagesForm(forms.ModelForm):
    # dam_OTL_pic = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    # lbimg_job_no = forms.CharField(widget=HiddenInput(), required=False)
    lbimg_inward_pod = forms.FileField(required=False)
    class Meta:
        model = Loadingbayimages_Info
        fields = '__all__'
        # fields=('dam_OTL_pic','dam_document')