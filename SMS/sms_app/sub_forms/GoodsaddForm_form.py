from django import forms
from ..models import Warehouse_goods_info

class GoodsaddForm(forms.ModelForm):
    class Meta:
        model = Warehouse_goods_info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(GoodsaddForm, self).__init__(*args, **kwargs)
        self.fields['wh_goods_package_type'].empty_label = "--Select--"
        self.fields['wh_goods_status'].empty_label = "--Select--"
        self.fields['wh_weights_deviation'].empty_label = "--Select--"
        self.fields['wh_dimension_deviation'].empty_label = "--Select--"
        self.fields['wh_no_of_units_deviation'].empty_label = "--Select--"
        self.fields['wh_damages'].empty_label = "--Select--"
        self.fields['wh_mismatches'].empty_label = "--Select--"
        self.fields['wh_ratification_process'].empty_label = "--Select--"
