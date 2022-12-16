from django import forms
from django.forms import ClearableFileInput, HiddenInput

from ..models import DamagereportInfo,DamagereportImages

class DamagereportaddForm(forms.ModelForm):
    class Meta:
        model = DamagereportInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DamagereportaddForm, self).__init__(*args, **kwargs)
        self.fields['dam_damage_type'].empty_label = "--Select--"
        self.fields['dam_status'].empty_label = "--Select--"
        self.fields['dam_no_of_units_deviation'].empty_label = "--Select--"
        self.fields['dam_ratification_process'].empty_label = "--Select--"
        self.fields['dam_marks_numbers'].empty_label = "--Select--"

class DamagereportImagesForm(forms.ModelForm):
    # dam_OTL_pic = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
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
        # fields=('dam_OTL_pic','dam_document')


