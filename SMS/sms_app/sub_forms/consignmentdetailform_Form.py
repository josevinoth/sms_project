from django import forms


from ..models import ConsignmentdetailInfo

class ConsignmentdetailaddForm(forms.ModelForm):
    co_cusrefnum_check = forms.BooleanField(required=False)
    co_cusrefnum = forms.CharField(required=False)

    class Meta:
        model = ConsignmentdetailInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ConsignmentdetailaddForm,self).__init__(*args, **kwargs)
        self.fields['co_customer'].empty_label = "--Select--"
        self.fields['co_status'].empty_label = "--Select--"
        self.fields['co_cusrefnum'].empty_label = "--Select--"
        self.fields['co_gst_payable_by'].empty_label = "--Select--"
        self.fields['co_currency_type'].empty_label = "--Select--"

