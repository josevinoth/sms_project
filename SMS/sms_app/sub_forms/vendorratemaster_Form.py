from django import forms
from ..models import VendorratemasterInfo1


class VendorratemasteraddForm(forms.ModelForm):

    class Meta:
        model = VendorratemasterInfo1
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(VendorratemasteraddForm,self).__init__(*args, **kwargs)
        self.fields['vr1_fromlocation'].empty_label = "--Select--"
        self.fields['vr1_tolocation'].empty_label = "--Select--"
        self.fields['vr1_vehicletype'].empty_label = "--Select--"
        self.fields['vr1_vendor'].empty_label = "--Select--"
        self.fields['vr1_vehiclecategory'].empty_label = "--Select--"
        self.fields['vr1_touchpoint'].empty_label = "--Select--"
        self.fields['vr1_touchpoint2'].empty_label = "--Select--"
        self.fields['vr1_touchpoint3'].empty_label = "--Select--"
        self.fields['vr1_touchpoint4'].empty_label = "--Select--"
