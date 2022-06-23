from django import forms
from ..models import CustomerdepartmentInfo

class CustomerdepartmentaddForm(forms.ModelForm):
    class Meta:
        model = CustomerdepartmentInfo
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super(ProducttypeaddForm,self).__init__(*args, **kwargs)
    #     self.fields['prod_type_title'].empty_label = "--Select--"