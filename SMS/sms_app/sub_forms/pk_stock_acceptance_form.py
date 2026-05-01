from django import forms
from ..models import pk_stock_statusinfo, PkcostingInfo, PkpartcodeInfo

class PkacceptanceForm(forms.ModelForm):

    class Meta:
        model = PkcostingInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkacceptanceForm,self).__init__(*args, **kwargs)
        
        # Restrict PartCode to prevent loading 10k items
        if 'ct_part_code' in self.fields:
            self.fields['ct_part_code'].queryset = PkpartcodeInfo.objects.none()
            self.fields['ct_part_code'].choices = []

            # Handle submission (POST)
            submitted_data = args[0] if args else kwargs.get('data')
            if submitted_data and 'ct_part_code' in submitted_data:
                pid = submitted_data.get('ct_part_code')
                if pid:
                    self.fields['ct_part_code'].queryset = PkpartcodeInfo.objects.filter(pk=pid)

            if self.instance and self.instance.pk and self.instance.ct_part_code:
                self.fields['ct_part_code'].queryset = PkpartcodeInfo.objects.filter(pk=self.instance.ct_part_code.pk)
                self.fields['ct_part_code'].choices = [(self.instance.ct_part_code.pk, str(self.instance.ct_part_code))]
            
            if 'ct_part_code' in self.initial and self.initial['ct_part_code']:
                part_id = self.initial['ct_part_code']
                self.fields['ct_part_code'].queryset = PkpartcodeInfo.objects.filter(pk=part_id)
        self.fields['ct_stock_status'].empty_label = "--Select--"
        self.fields['ct_excess_status'].empty_label = "--Select--"
        self.fields['ct_stock_status'].queryset = pk_stock_statusinfo.objects.filter(id__in=[4])