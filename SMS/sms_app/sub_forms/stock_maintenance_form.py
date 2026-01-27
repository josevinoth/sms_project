from django import forms
from ..sub_models.stock_maintenance_mod import StockMaintenance
from ..sub_models.part_code_mod import PkpartcodeInfo


class StockMaintenanceForm(forms.ModelForm):

    # Override partcode field for better control
    sm_partcode = forms.ModelChoiceField(
        queryset=PkpartcodeInfo.objects.all(),
        required=True
    )

    class Meta:
        model = StockMaintenance
        fields = '__all__'

        # Exclude auto-filled/system fields
        exclude = (
            'sm_created_at',
            'sm_updated_at',
            'sm_updated_by',
        )

        widgets = {
            'sm_invoice_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sm_uom'].widget = forms.HiddenInput()


        self.fields['sm_stock_type'].empty_label = "--Select Stock Type--"
        self.fields['sm_partcode'].empty_label = "--Select Partcode--"

        # Use the part code as the value (pc_code is a unique CharField)
        # if 'sm_partcode' in self.fields:
             # self.fields['sm_partcode'].to_field_name = "pc_code"

        # ===================================
        # READONLY FIELDS (Auto-filled)
        # ===================================
        readonly_fields = [
            'sm_description',
            'sm_thickness',
            'sm_width',
            'sm_length',
            'sm_uom',
            'sm_cft',
            'sm_total_price',
            "sm_total_cft",
        ]

        for field_name in readonly_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['readonly'] = 'readonly'
                self.fields[field_name].widget.attrs['class'] = 'form-control disable_a_href'



