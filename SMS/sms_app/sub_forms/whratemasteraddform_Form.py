from django import forms
from ..models import WhratemasterInfo

class WhratemasteraddForm(forms.ModelForm):
    class Meta:
        model = WhratemasterInfo
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super(GoodsaddForm, self).__init__(*args, **kwargs)
    #     self.fields['wh_goods_package_type'].empty_label = "--Select--"