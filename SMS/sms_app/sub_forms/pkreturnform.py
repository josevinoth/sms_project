from django import forms
from ..models import PkcostingInfo,ExcessStock

class PkreturnForm(forms.ModelForm):

    class Meta:
        model = PkcostingInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkreturnForm,self).__init__(*args, **kwargs)
        self.fields['ct_excess_status'].empty_label = "--Select--"
        self.fields['ct_excess_status'].queryset = ExcessStock.objects.filter(id__in=[4])