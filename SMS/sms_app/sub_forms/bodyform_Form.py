from django import forms
from ..models import BodyInfo

class BodyaddForm(forms.ModelForm):
    class Meta:
        model = BodyInfo
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super(ProducttypeaddForm,self).__init__(*args, **kwargs)
    #     self.fields['prod_type_title'].empty_label = "--Select--"