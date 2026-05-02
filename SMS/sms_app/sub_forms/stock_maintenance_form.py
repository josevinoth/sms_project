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

        # Forcibly clear choices to prevent rendering 10k options in HTML
        self.fields['sm_partcode'].queryset = PkpartcodeInfo.objects.none()
        self.fields['sm_partcode'].choices = [('', '--Select Partcode--')]

        # Handle submission (POST) - Allow the submitted ID to pass validation
        if args and args[0] and 'sm_partcode' in args[0]:
            pid = args[0].get('sm_partcode')
            if pid:
                self.fields['sm_partcode'].queryset = PkpartcodeInfo.objects.filter(pk=pid)

        # If editing (instance exists), add the current partcode back
        elif self.instance and self.instance.pk and self.instance.sm_partcode:
            self.fields['sm_partcode'].queryset = PkpartcodeInfo.objects.filter(pk=self.instance.sm_partcode.pk)
            self.fields['sm_partcode'].choices = [
                ('', '--Select Partcode--'),
                (self.instance.sm_partcode.pk, str(self.instance.sm_partcode.pc_code))
            ]
        # If initial data (sticky data) exists
        elif 'sm_partcode' in self.initial and self.initial['sm_partcode']:
            try:
                pid = self.initial['sm_partcode']
                part = PkpartcodeInfo.objects.get(pk=pid)
                self.fields['sm_partcode'].queryset = PkpartcodeInfo.objects.filter(pk=pid)
                self.fields['sm_partcode'].choices = [
                    ('', '--Select Partcode--'),
                    (part.pk, str(part.pc_code))
                ]
            except:
                pass

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



