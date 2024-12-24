from django import forms
from ..models import ExcessStock,PkcostingInfo

class PkexcessForm(forms.ModelForm):

    class Meta:
        model = PkcostingInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkexcessForm,self).__init__(*args, **kwargs)
        self.fields['ct_excess_status'].empty_label = "--Select--"
        self.fields['ct_excess_status'].queryset = ExcessStock.objects.filter(id__in=[1,2,4])