from django import forms
from ..models import PkstockpurchasesInfo

class PkreturnForm(forms.ModelForm):
    class Meta:
        model = PkstockpurchasesInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkreturnForm, self).__init__(*args, **kwargs)
        self.fields['sp_status'].empty_label = "--Select--"
        self.fields['sp_status'].queryset = PkstockpurchasesInfo.objects.filter(sp_status=2)
