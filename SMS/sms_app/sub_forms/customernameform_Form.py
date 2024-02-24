from django import forms
from ..models import CustomernameInfo_new

class CustomernameaddForm(forms.ModelForm):
    class Meta:
        model = CustomernameInfo_new
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super(ProducttypeaddForm,self).__init__(*args, **kwargs)
    #     self.fields['prod_type_title'].empty_label = "--Select--"