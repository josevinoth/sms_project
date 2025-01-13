from django import forms

from ..models import warehouse_goodsnew_info

class warehouse_goodsadd_gatein_form(forms.ModelForm):
    class Meta:
        model = warehouse_goodsnew_info
        fields = ['whn_po_num','whn_fumigation_date','whn_job_no','whn_uom','whn_goods_pieces','whn_goods_length','whn_goods_width','whn_goods_height','whn_goods_weight','whn_goods_package_type','whn_goods_area','whn_goods_volume_weight','whn_chargeable_weight','whn_cbm','whn_weights_deviation','whn_dimension_deviation','whn_no_of_units_deviation','whn_damages','whn_mismatches','whn_fumigation_process','whn_fumigation_action','whn_goods_status','whn_customer_name','whn_customer_type','whn_goods_invoice','whn_qr_rand_num','whn_consigner','whn_consignee','whn_comments','whn_checkin_time','whn_po_num','whn_job_no', 'whn_uom', 'whn_goods_pieces', 'whn_goods_length', 'whn_goods_width', 'whn_goods_height',
                  'whn_goods_weight', 'whn_goods_package_type', 'whn_goods_area', 'whn_goods_volume_weight',
                  'whn_chargeable_weight', 'whn_cbm', 'whn_weights_deviation', 'whn_dimension_deviation',
                  'whn_no_of_units_deviation', 'whn_damages', 'whn_mismatches',
                  'whn_branch','whn_unit','whn_bay','whn_available_area','whn_available_volume','whn_check_in_out','whn_customer_name','whn_customer_type','whn_goods_invoice','whn_stack_layer','whn_qr_rand_num','whn_consigner','whn_consignee']
        # fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['whn_goods_package_type'].empty_label = "--Select--"
        self.fields['whn_goods_status'].empty_label = "--Select--"
        self.fields['whn_weights_deviation'].empty_label = "--Select--"
        self.fields['whn_dimension_deviation'].empty_label = "--Select--"
        self.fields['whn_no_of_units_deviation'].empty_label = "--Select--"
        self.fields['whn_damages'].empty_label = "--Select--"
        self.fields['whn_mismatches'].empty_label = "--Select--"
        self.fields['whn_fumigation_process'].empty_label = "--Select--"
        self.fields['whn_fumigation_action'].empty_label = "--Select--"
        self.fields['whn_uom'].empty_label = "--Select--"
        self.fields['whn_customer_name'].empty_label = "--Select--"
        self.fields['whn_customer_type'].empty_label = "--Select--"






