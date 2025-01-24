from django import forms

from ..models import warehouse_goodsnew_info

class warehouse_goodsadd_gatein_form(forms.ModelForm):
    class Meta:
        model = warehouse_goodsnew_info
        fields = ['whn_gatein_status','whn_truck_number_n','whn_pre_id','whn_hawb','whn_cargo','whn_dock_in_date_time','whn_consigner','whn_consignee','whn_total_qty','whn_gross_weight','whn_destination','whn_updated_by','whn_comodity','whn_department','whn_customer_type','whn_customer_name','whn_po_num','whn_goods_invoice','whn_job_no']
        # fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['whn_customer_name'].empty_label = "--Select--"
        self.fields['whn_customer_type'].empty_label = "--Select--"
        self.fields['whn_comodity'].empty_label = "--Select--"
        self.fields['whn_cargo'].empty_label = "--Select--"
        self.fields['whn_gatein_status'].empty_label = "--Select--"






