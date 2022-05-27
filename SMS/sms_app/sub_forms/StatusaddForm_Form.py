from django import forms
from ..models import StatusInfo

class StatusaddForm(forms.ModelForm):
    class Meta:
        model = StatusInfo
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super(ProducttypeaddForm,self).__init__(*args, **kwargs)
    #     self.fields['prod_type_title'].empty_label = "--Select--"