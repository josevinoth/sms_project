from django import forms
from ..models import task_Info,RequirementsInfo

class taskaddForm(forms.ModelForm):
    class Meta:
        model = task_Info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(taskaddForm,self).__init__(*args, **kwargs)
        self.fields['application'].empty_label = "--Select--"
        self.fields['t_requirement_id'].empty_label = "--Select--"
        self.fields['t_requirement_id'].queryset = RequirementsInfo.objects.filter(req_status=6)
        # self.fields['Bay_unit_name'].empty_label = "--Select--"