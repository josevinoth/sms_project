from django import forms
from ..models import BusinessrevenueInfo

class BusinessrevenueForm(forms.ModelForm):
    class Meta:
        model = BusinessrevenueInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BusinessrevenueForm,self).__init__(*args, **kwargs)
        self.fields['br_customer_name'].empty_label = "--Select--"
        self.fields['br_business'].empty_label = "--Select--"
        self.fields['br_sale_person'].empty_label = "--Select--"
        self.fields['br_updated_by'].empty_label = "--Select--"
