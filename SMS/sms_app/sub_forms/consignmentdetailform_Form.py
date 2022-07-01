from django import forms
from ..models import ConsignmentdetailInfo

class ConsignmentdetailaddForm(forms.ModelForm):

    class Meta:
        model = ConsignmentdetailInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ConsignmentdetailaddForm,self).__init__(*args, **kwargs)
        self.fields['co_movement'].empty_label = "--Select--"
        self.fields['co_status'].empty_label = "--Select--"
