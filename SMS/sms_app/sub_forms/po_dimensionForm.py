from django import forms
from ..models import POdimension,Nadimension

class POdimensionForm(forms.ModelForm):
    class Meta:
        model = POdimension
        exclude = ['pod_updated_by']

    def __init__(self, *args, **kwargs):
        super(POdimensionForm,self).__init__(*args, **kwargs)
        self.fields['pod_assess_num'].empty_label = "--Select--"
        self.fields['pod_type_of_req'].empty_label = "--Select--"
        self.fields['pod_uom'].empty_label = "--Select--"
        self.fields['pod_plywood_thickness'].empty_label = "--Select--"
        self.fields['pod_wood_type'].empty_label = "--Select--"
        self.fields['pod_wood_description'].empty_label = "--Select--"
        self.fields['pod_nad'].empty_label = "--Select--"
