from django import forms
from ..models import Sales_Comments_Info
class SalescommentForm(forms.ModelForm):
    class Meta:
        model = Sales_Comments_Info
        fields = '__all__'
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
        }

    def __init__(self, *args, **kwargs):
        super(SalescommentForm,self).__init__(*args, **kwargs)
        self.fields['sc_call_type'].empty_label = "--Select--"
        self.fields['sc_call_nature'].empty_label = "--Select--"
        self.fields['sc_call_purpose'].empty_label = "--Select--"