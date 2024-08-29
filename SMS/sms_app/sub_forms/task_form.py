from django import forms
from ..models import task_Info

class taskaddForm(forms.ModelForm):
    class Meta:
        model = task_Info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(taskaddForm,self).__init__(*args, **kwargs)
        self.fields['application'].empty_label = "--Select--"
        # self.fields['Bay_unit_name'].empty_label = "--Select--"