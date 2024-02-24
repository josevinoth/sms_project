from django import forms
from ..models import Product_info

class ProductaddForm(forms.ModelForm):
    class Meta:
        model = Product_info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProductaddForm,self).__init__(*args, **kwargs)
        # self.fields['prod_category'].empty_label = "--Select--"
        self.fields['prod_type'].empty_label = "--Select--"