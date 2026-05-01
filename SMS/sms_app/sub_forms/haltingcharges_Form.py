from django import forms
from ..models import EnquirynoteInfo
from ..sub_models.haltingcharges_mod import Haltingcharges


class HaltingchargesForm(forms.ModelForm):

    class Meta:
        model = Haltingcharges
        exclude = ('hc_updated_at', 'hc_updated_by')

    def __init__(self, *args, **kwargs):
        super(HaltingchargesForm,self).__init__(*args, **kwargs)
        self.fields['hc_Customer_name'].empty_label = "--Select--"
        self.fields['hc_Customer_name'].queryset = self.fields['hc_Customer_name'].queryset.filter(cu_name__icontains='(T)')
        self.fields['hc_trip_type'].empty_label = "--Select--"
