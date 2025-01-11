from django import forms
from ..models import Warehouse_goods_new_info

class WarehousegoodsnewForm(forms.ModelForm):
    class Meta:
        model = Warehouse_goods_new_info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(WarehousegoodsnewForm,self).__init__(*args, **kwargs)
        self.fields['wh_new_check_in_out'].empty_label = "--Select--"
        self.fields['wh_new_goods_status'].empty_label = "--Select--"

