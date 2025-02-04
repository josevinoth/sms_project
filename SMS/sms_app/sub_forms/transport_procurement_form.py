from django import forms
from django.utils import timezone

from ..models import Vehicle_procurementInfo

class vechicle_procurementForm(forms.ModelForm):
    vp_current = forms.DateField(
        initial=timezone.now().strftime('%Y-%m-%d'),  # Format date as 'YYYY-MM-DD'
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    class Meta:
        model = Vehicle_procurementInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(vechicle_procurementForm,self).__init__(*args, **kwargs)
        self.fields['vp_vendor_name'].empty_label = "--Select--"
        self.fields['vp_fromlocaion'].empty_label = "--Select--"
        self.fields['vp_tolocation'].empty_label = "--Select--"
        self.fields['vp_vehicletype'].empty_label = "--Select--"
        self.fields['vp_updated_by'].empty_label = "--Select--"