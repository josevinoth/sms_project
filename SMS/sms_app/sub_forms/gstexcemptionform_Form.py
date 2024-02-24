from django import forms
from ..models import GstexcemptionInfo

class GstexcemptionForm(forms.ModelForm):
    class Meta:
        model = GstexcemptionInfo
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super(ProducttypeaddForm,self).__init__(*args, **kwargs)
    #     self.fields['prod_type_title'].empty_label = "--Select--"