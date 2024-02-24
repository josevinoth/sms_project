from django import forms
from ..models import Warehouse_stock_info

class StockaddForm(forms.ModelForm):
    class Meta:
        model = Warehouse_stock_info
        fields = '__all__'

        def __init__(self, *args, **kwargs):
            super(StockaddForm, self).__init__(*args, **kwargs)
            # self.fields['wh_stock_movement_type'].empty_label = "--Select--"
            self.fields['wh_stock_type'].empty_label = "--Select--"
            self.fields['wh_stock_invoice_currency'].empty_label = "--Select--"