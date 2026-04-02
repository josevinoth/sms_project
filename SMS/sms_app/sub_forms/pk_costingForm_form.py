from django import forms
from ..models import PkcostingInfo, Nadimension, PkpurchaseorderInfo, POdimension

class PkcostingForm(forms.ModelForm):

    class Meta:
        model = PkcostingInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        assessment_id = kwargs.pop('assessment_id', None)

        # Get from POST if not passed
        if not assessment_id and 'data' in kwargs:
            assessment_id = kwargs['data'].get('ct_assessment_num')

        super().__init__(*args, **kwargs)

        if assessment_id:
            self.fields['ct_requirement'].queryset = Nadimension.objects.filter(nad_assess_num=assessment_id)
            self.fields['ct_customer_po'].queryset = PkpurchaseorderInfo.objects.filter(po_assessment_num=assessment_id)
            self.fields['ct_po_dimension'].queryset = POdimension.objects.filter(pod_assess_num=assessment_id)
        else:
            self.fields['ct_requirement'].queryset = Nadimension.objects.all()
            self.fields['ct_customer_po'].queryset = PkpurchaseorderInfo.objects.all()
            self.fields['ct_po_dimension'].queryset = POdimension.objects.all()

        # Labels
        self.fields['ct_customer_name'].empty_label = "--Select--"
        self.fields['ct_customer_po'].empty_label = "--Select--"
        self.fields['ct_cost_type'].empty_label = "--Select--"
        self.fields['ct_stock_type'].empty_label = "--Select--"
        self.fields['ct_stock_description'].empty_label = "--Select--"
        self.fields['ct_updated_by'].empty_label = "--Select--"
        self.fields['ct_uom'].empty_label = "--Select--"
        self.fields['ct_assessment_num'].empty_label = "--Select--"
        self.fields['ct_item'].empty_label = "--Select--"
        self.fields['ct_itemdescription'].empty_label = "--Select--"
        self.fields['ct_requirement'].empty_label = "--Select--"
        self.fields['ct_stock_status'].empty_label = "--Select--"
        self.fields['ct_stock_purchase_number'].empty_label = "--Select--"
        self.fields['ct_excess_status'].empty_label = "--Select--"
        self.fields['ct_grn'].empty_label = "--Select--"
        self.fields['ct_weight_received'].empty_label = "--Select--"
        self.fields['ct_weight_Consumption'].empty_label = "--Select--"