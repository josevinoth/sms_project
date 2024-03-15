from django import forms
from ..models import PkneedassessmentInfo

class PkneedassessmentForm(forms.ModelForm):

    class Meta:
        model = PkneedassessmentInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkneedassessmentForm,self).__init__(*args, **kwargs)
        self.fields['na_customer_name'].empty_label = "--Select--"
        self.fields['na_type_of_work'].empty_label = "--Select--"
        self.fields['na_type_of_pack'].empty_label = "--Select--"
        self.fields['na_wood_treatment_req'].empty_label = "--Select--"
        self.fields['na_unloading'].empty_label = "--Select--"
        self.fields['na_wood_norms'].empty_label = "--Select--"
        self.fields['na_vehicle'].empty_label = "--Select--"
        self.fields['na_vehicle_type'].empty_label = "--Select--"
        self.fields['na_type_of_access'].empty_label = "--Select--"
        self.fields['na_consumables'].empty_label = "--Select--"
        self.fields['na_updated_by'].empty_label = "--Select--"
        self.fields['na_status'].empty_label = "--Select--"
