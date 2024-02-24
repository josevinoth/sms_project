from django import forms
from ..models import WhstoragetypeInfo

class WhstoragetypeaddForm(forms.ModelForm):
    class Meta:
        model = WhstoragetypeInfo
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super(ProducttypeaddForm,self).__init__(*args, **kwargs)
    #     self.fields['prod_type_title'].empty_label = "--Select--"