from django import forms
from django.forms import ClearableFileInput, HiddenInput
from ..models import DamagereportInfo, DamagereportImages

class DamagereportaddForm(forms.ModelForm):
    # New fields
    dam_no_of_pcs_damaged = forms.IntegerField(
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'id': 'dam_no_of_pcs_damaged', 'class': 'form-control', 'min': '0'})
    )
    dam_invoice_weight = forms.FloatField(
        required=False,
        initial=0.0,
        widget=forms.NumberInput(attrs={'id': 'dam_invoice_weight', 'class': 'form-control', 'readonly': 'readonly', 'step': 'any'})
    )
    dam_checkin_weight = forms.FloatField(
        required=False,
        initial=0.0,
        widget=forms.NumberInput(attrs={'id': 'dam_checkin_weight', 'class': 'form-control', 'step': 'any'})
    )
    dam_invoice_qty = forms.IntegerField(
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'id': 'dam_invoice_qty', 'class': 'form-control', 'readonly': 'readonly'})
    )
    dam_checkin_qty = forms.IntegerField(
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'id': 'dam_checkin_qty', 'class': 'form-control'})
    )

    class Meta:
        model = DamagereportInfo
        fields = '__all__'
        widgets = {
            'dam_damages1': forms.SelectMultiple(attrs={'id': 'dam_damages1', 'class': 'form-control'}),
            'dam_deviation1': forms.SelectMultiple(attrs={'id': 'dam_deviation1', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(DamagereportaddForm, self).__init__(*args, **kwargs)
        self.fields['dam_status'].empty_label = "--Select--"
        self.fields['dam_no_of_units_deviation'].empty_label = "--Select--"
        self.fields['dam_ratification_process'].empty_label = "--Select--"
        self.fields['dam_marks_numbers'].empty_label = "--Select--"
        # ⚡ removed empty_label for dam_damage_type, because SelectMultiple does not support empty_label

class DamagereportImagesForm(forms.ModelForm):
    damimage_wh_job_num = forms.CharField(widget=HiddenInput(), required=False)
    dam_OTL_pic = forms.FileField(required=False)
    dam_document = forms.FileField(required=False)
    dam_open_door_pic = forms.FileField(required=False)
    dam_50_offload_pic = forms.FileField(required=False)
    dam_empty_vehicle = forms.FileField(required=False)
    dam_closed_door_pic = forms.FileField(required=False)
    dam_customer_approval = forms.FileField(required=False)

    class Meta:
        model = DamagereportImages
        fields = '__all__'
