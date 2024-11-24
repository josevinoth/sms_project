from django import forms
from ..models import BudgetInfo

class BudgetForm(forms.ModelForm):
    class Meta:
        model = BudgetInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BudgetForm,self).__init__(*args, **kwargs)
        self.fields['bf_updated_by'].empty_label = "--Select--"
