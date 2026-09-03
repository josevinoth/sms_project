from django import forms
from ..models import PkquotationInfo, PkpartcodeInfo

class PkquotationForm(forms.ModelForm):

    class Meta:
        model = PkquotationInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkquotationForm,self).__init__(*args, **kwargs)
        
        # Restrict PartCode to prevent loading 10k items
        self.fields['pkqt_part_code'].queryset = PkpartcodeInfo.objects.none()
        self.fields['pkqt_part_code'].choices = []

        # Handle submission (POST)
        submitted_data = args[0] if args else kwargs.get('data')
        if submitted_data and 'pkqt_part_code' in submitted_data:
            pid = submitted_data.get('pkqt_part_code')
            if pid:
                self.fields['pkqt_part_code'].queryset = PkpartcodeInfo.objects.filter(pk=pid)

        if self.instance and self.instance.pk and self.instance.pkqt_part_code:
            self.fields['pkqt_part_code'].queryset = PkpartcodeInfo.objects.filter(pk=self.instance.pkqt_part_code.pk)
            self.fields['pkqt_part_code'].choices = [(self.instance.pkqt_part_code.pk, str(self.instance.pkqt_part_code))]
        
        if 'pkqt_part_code' in self.initial and self.initial['pkqt_part_code']:
            part_id = self.initial['pkqt_part_code']
            part_obj = PkpartcodeInfo.objects.filter(pk=part_id).first()
            if part_obj:
                self.fields['pkqt_part_code'].queryset = PkpartcodeInfo.objects.filter(pk=part_id)
                self.fields['pkqt_part_code'].choices = [(part_obj.pk, str(part_obj))]
        self.fields['pkqt_cost_type'].empty_label = "--Select--"
        self.fields['pkqt_stock_type'].empty_label = "--Select--"
        self.fields['pkqt_stock_description'].empty_label = "--Select--"
        self.fields['pkqt_updated_by'].empty_label = "--Select--"
        self.fields['pkqt_uom'].empty_label = "--Select--"
        self.fields['pkqt_assessment_num'].empty_label = "--Select--"
        self.fields['pkqt_requirement'].empty_label = "--Select--"
        self.fields['pkqt_item'].empty_label = "--Select--"
        self.fields['pkqt_itemdescription'].empty_label = "--Select--"
        self.fields['pkqt_stock_purchase_number'].empty_label = "--Select--"
        self.fields['pkqt_part_code'].empty_label = "--Select--"
        self.fields['pkqt_weight_received'].empty_label = "--Select--"
        self.fields['pkqt_weight_Consumption'].empty_label = "--Select--"
