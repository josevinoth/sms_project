from django import forms
from ..models import Warehouse_goods_info,UnitInfo,StatusList,BayInfo,LocationmasterInfo

class WarehoseinaddForm(forms.ModelForm):
    class Meta:
        model = Warehouse_goods_info
        fields = ['wh_job_no', 'wh_uom', 'wh_goods_pieces', 'wh_goods_length', 'wh_goods_width', 'wh_goods_height',
                  'wh_goods_weight', 'wh_goods_package_type', 'wh_goods_area', 'wh_goods_volume_weight',
                  'wh_chargeable_weight', 'wh_CBM', 'wh_weights_deviation', 'wh_dimension_deviation',
                  'wh_no_of_units_deviation', 'wh_damages', 'wh_mismatches',
                  'wh_branch','wh_unit','wh_bay','wh_available_area','wh_available_volume','wh_check_in_out','wh_customer_name','wh_customer_type','wh_goods_invoice','wh_stack_layer','wh_qr_rand_num','wh_consigner','wh_consignee']

        # fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['wh_goods_package_type'].empty_label = "--Select--"
        self.fields['wh_weights_deviation'].empty_label = "--Select--"
        self.fields['wh_dimension_deviation'].empty_label = "--Select--"
        self.fields['wh_no_of_units_deviation'].empty_label = "--Select--"
        self.fields['wh_damages'].empty_label = "--Select--"
        self.fields['wh_mismatches'].empty_label = "--Select--"
        # self.fields['wh_ratification_process'].empty_label = "--Select--"
        self.fields['wh_check_in_out'].required = True
        self.fields['wh_stack_layer'].empty_label = "--Select--"
        self.fields['wh_branch'].empty_label = "--Select--"
        self.fields['wh_unit'].empty_label = "--Select--"