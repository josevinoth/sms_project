from django import forms
from django_select2.forms import Select2MultipleWidget
from ..models import PkneedassessmentInfo
from ..sub_models.na_typeofaccess_mod import Natypeofaccess


class PkneedassessmentForm(forms.ModelForm):
    # Many-to-Many field for multiple selections
    na_type_of_access = forms.ModelMultipleChoiceField(
        queryset=Natypeofaccess.objects.all(),
        widget=Select2MultipleWidget(),  # Optional: provides enhanced multi-select UI
        required=False
    )

    class Meta:
        model = PkneedassessmentInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PkneedassessmentForm, self).__init__(*args, **kwargs)
        self.fields['na_customer_name'].empty_label = "--Select--"
        self.fields['na_type_of_work'].empty_label = "--Select--"
        self.fields['na_type_of_pack'].empty_label = "--Select--"
        self.fields['na_wood_treatment_req'].empty_label = "--Select--"
        # self.fields['na_special_requirements'].empty_label = "--Select--"
        self.fields['na_unloading'].empty_label = "--Select--"
        # self.fields['na_wood_norms'].empty_label = "--Select--"
        self.fields['na_delivery_by'].empty_label = "--Select--"
        self.fields['na_delivery_type'].empty_label = "--Select--"
        self.fields['na_vehicle_type'].empty_label = "--Select--"
        # Commented out since ManyToManyField does not need an empty label
        # self.fields['na_type_of_access'].empty_label = "--Select--"
        # self.fields['na_consumables'].empty_label = "--Select--"
        self.fields['na_packing_field'].empty_label = "--Select--"
        self.fields['na_updated_by'].empty_label = "--Select--"
        self.fields['na_status'].empty_label = "--Select--"
