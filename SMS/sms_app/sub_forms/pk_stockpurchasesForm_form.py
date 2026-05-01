from django import forms
from ..models import PkstockpurchasesInfo, PkpartcodeInfo

class PkstockpurchasesForm(forms.ModelForm):

    class Meta:
        model = PkstockpurchasesInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkstockpurchasesForm,self).__init__(*args, **kwargs)
        
        # Restrict PartCode to prevent loading 10k items
        self.fields['sp_part_code'].queryset = PkpartcodeInfo.objects.none()
        self.fields['sp_part_code'].choices = []

        # Handle submission (POST)
        submitted_data = args[0] if args else kwargs.get('data')
        if submitted_data and 'sp_part_code' in submitted_data:
            pid = submitted_data.get('sp_part_code')
            if pid:
                self.fields['sp_part_code'].queryset = PkpartcodeInfo.objects.filter(pk=pid)

        if self.instance and self.instance.pk and self.instance.sp_part_code:
            self.fields['sp_part_code'].queryset = PkpartcodeInfo.objects.filter(pk=self.instance.sp_part_code.pk)
            self.fields['sp_part_code'].choices = [(self.instance.sp_part_code.pk, str(self.instance.sp_part_code))]
        
        if 'sp_part_code' in self.initial and self.initial['sp_part_code']:
            part_id = self.initial['sp_part_code']
            self.fields['sp_part_code'].queryset = PkpartcodeInfo.objects.filter(pk=part_id)
        self.fields['sp_category'].empty_label = "--Select--"
        self.fields['sp_source'].empty_label = "--Select--"
        self.fields['sp_updated_by'].empty_label = "--Select--"
        self.fields['sp_stock_description'].empty_label = "--Select--"
        self.fields['sp_uom'].empty_label = "--Select--"
        self.fields['sp_stock_type'].empty_label = "--Select--"
        self.fields['sp_status'].empty_label = "--Select--"
        self.fields['sp_status'].initial = 1
        self.fields['sp_part_code'].empty_label = "--Select--"
        self.fields['sp_vendor_bill_id'].empty_label = "--Select--"
