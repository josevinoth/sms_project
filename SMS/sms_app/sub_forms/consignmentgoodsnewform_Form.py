from django import forms
from ..models import consignmentsgoods_new_info

class ConsignmentgoodsnewaddForm(forms.ModelForm):
    class Meta:
        model = consignmentsgoods_new_info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ConsignmentgoodsnewaddForm,self).__init__(*args, **kwargs)
        self.fields['cn_consignment_num'].empty_label = "--Select--"
        self.fields['cn_lastmodifiedby'].empty_label = "--Select--"
