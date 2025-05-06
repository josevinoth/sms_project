from django import forms
from ..models import Nadimension,Pkstocktype

class NadimensionForm(forms.ModelForm):
    class Meta:
        model = Nadimension
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(NadimensionForm,self).__init__(*args, **kwargs)
        self.fields['nad_assess_num'].empty_label = "--Select--"
        self.fields['nad_type_of_req'].empty_label = "--Select--"
        self.fields['nad_uom'].empty_label = "--Select--"
        self.fields['nad_plywood_thickness'].empty_label = "--Select--"
        self.fields['nad_wood_type'].queryset = Pkstocktype.objects.filter(id__in=[1, 4])
        self.fields['nad_dimension_type'].empty_label = "--Select--"
        self.fields['nad_consumables'].empty_label = "--Select--"
        self.fields['nad_vechicle_type'].empty_label = "--Select--"