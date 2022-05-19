from django import forms
from ..models import Warehouse_goods_info

class GoodsaddForm(forms.ModelForm):
    class Meta:
        model = Warehouse_goods_info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(GoodsaddForm, self).__init__(*args, **kwargs)
        self.fields['wh_goods_package_type'].empty_label = "--Select--"