from django import forms
from ..models import PkpartcodeInfo

class Part_codeForm(forms.ModelForm):
    class Meta:
        model = PkpartcodeInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(Part_codeForm, self).__init__(*args, **kwargs)
        self.fields['pc_stock_type'].empty_label = "--Select--"
        self.fields['pc_stock_description'].empty_label = "--Select--"
        self.fields['pc_uom'].empty_label = "--Select--"

    def clean_pc_code(self):
        pc_code = self.cleaned_data.get('pc_code', '').strip().upper()
        self.cleaned_data['pc_code'] = pc_code  # Normalize and set back

        qs = PkpartcodeInfo.objects.filter(pc_code=pc_code)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)  # Exclude current instance on update

        if qs.exists():
            raise forms.ValidationError("Part Code already exists.")
        return pc_code
