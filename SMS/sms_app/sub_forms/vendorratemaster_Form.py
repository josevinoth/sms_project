from django import forms
from ..models import VendorratemasterInfo


class VendorratemasteraddForm(forms.ModelForm):

    class Meta:
        model = VendorratemasterInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(VendorratemasteraddForm,self).__init__(*args, **kwargs)
        self.fields['vr_fromlocation'].empty_label = "--Select--"
        self.fields['vr_tolocation'].empty_label = "--Select--"
        self.fields['vr_vehicletype'].empty_label = "--Select--"
        self.fields['vr_vendor'].empty_label = "--Select--"
        self.fields['vr_vehiclecategory'].empty_label = "--Select--"
        self.fields['vr_touchpoint'].empty_label = "--Select--"
        self.fields['vr_touchpoint2'].empty_label = "--Select--"
        self.fields['vr_touchpoint3'].empty_label = "--Select--"
        self.fields['vr_touchpoint4'].empty_label = "--Select--"
