from django import forms
from ..models import PkcostingInfo, Nadimension, PkpurchaseorderInfo, POdimension, PkpartcodeInfo

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
        
        # Restrict PartCode to prevent loading 10k items
        self.fields['ct_part_code'].queryset = PkpartcodeInfo.objects.none()
        self.fields['ct_part_code'].choices = []

        # Handle submission (POST)
        submitted_data = args[0] if args else kwargs.get('data')
        if submitted_data and 'ct_part_code' in submitted_data:
            pid = submitted_data.get('ct_part_code')
            if pid:
                self.fields['ct_part_code'].queryset = PkpartcodeInfo.objects.filter(pk=pid)
        
        if submitted_data and 'ct_stock_purchase_number' in submitted_data:
            sid = submitted_data.get('ct_stock_purchase_number')
            if sid:
                # Include StockMaintenance in the queryset for validation
                from ..models import StockMaintenance
                self.fields['ct_stock_purchase_number'].queryset = StockMaintenance.objects.filter(pk=sid)

        # If we have an instance (editing), ensure the current value is available
        if self.instance and self.instance.pk and self.instance.ct_part_code:
            self.fields['ct_part_code'].queryset = PkpartcodeInfo.objects.filter(pk=self.instance.ct_part_code.pk)
            self.fields['ct_part_code'].choices = [(self.instance.ct_part_code.pk, str(self.instance.ct_part_code))]
        
        # Also check initial for part_code (standard for these modules)
        if 'ct_part_code' in self.initial and self.initial['ct_part_code']:
            part_id = self.initial['ct_part_code']
            self.fields['ct_part_code'].queryset = PkpartcodeInfo.objects.filter(pk=part_id)
            # choices will be set by widget or manually if needed

        # Restrict/prepare ct_requirement queryset to avoid validation errors when a choice is posted
        # Default to none to avoid loading many Nadimension records
        self.fields['ct_requirement'].queryset = Nadimension.objects.none()
        # If assessment_id is known, expose Nadimension entries for that assessment
        try:
            if assessment_id:
                self.fields['ct_requirement'].queryset = Nadimension.objects.filter(nad_assess_num=assessment_id).order_by('id')
        except Exception:
            # fallback: keep empty queryset
            pass
        # If form was submitted and a ct_requirement value exists in POST, ensure that specific choice is included
        if submitted_data and 'ct_requirement' in submitted_data:
            try:
                rid = submitted_data.get('ct_requirement')
                if rid:
                    # Include the specific Nadimension even if it wasn't in the filtered queryset
                    req_qs = Nadimension.objects.filter(pk=rid)
                    if req_qs.exists():
                        # Combine querysets (use union if prior queryset populated)
                        self.fields['ct_requirement'].queryset = req_qs | self.fields['ct_requirement'].queryset
            except Exception:
                pass

        if assessment_id:
            self.fields['ct_customer_po'].queryset = PkpurchaseorderInfo.objects.filter(po_assessment_num=assessment_id)
            self.fields['ct_po_dimension'].queryset = POdimension.objects.filter(pod_assess_num=assessment_id)
        else:
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