from django import forms
from ..models import ConsignmentdetailInfo

class ConsignmentdetailaddForm(forms.ModelForm):

    class Meta:
        model = ConsignmentdetailInfo
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super(AssetinfoaddForm,self).__init__(*args, **kwargs)
    #     self.fields['asset_product'].empty_label = "--Select--"
    #     self.fields['asset_location'].empty_label = "--Select--"
    #     self.fields['asset_vendor'].empty_label = "--Select--"
    #     self.fields['asset_insurance_details'].empty_label = "--Select--"
    #     self.fields['asset_assignedto'].empty_label = "--Select--"
    #     self.fields['asset_assignedto'].required = False
    #     self.fields['asset_unit'].empty_label = "--Select--"