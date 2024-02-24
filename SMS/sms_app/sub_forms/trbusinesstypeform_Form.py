from django import forms
from ..models import TrbusinesstypeInfo

class TrbusinesstypeaddForm(forms.ModelForm):
    class Meta:
        model = TrbusinesstypeInfo
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super(ProducttypeaddForm,self).__init__(*args, **kwargs)
    #     self.fields['prod_type_title'].empty_label = "--Select--"