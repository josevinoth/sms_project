from django import forms
from ..models import MyUser,Sales_Comments_Info

class SalescommentForm(forms.ModelForm):
    class Meta:
        model = Sales_Comments_Info
        fields = '__all__'
        widgets = {
            'sc_comments': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
            'sc_joint_call_name': forms.SelectMultiple(),  # This ensures a multi-select widget is rendered
        }

    def __init__(self, *args, **kwargs):
        super(SalescommentForm, self).__init__(*args, **kwargs)
        self.fields['sc_call_type'].empty_label = "--Select--"
        self.fields['sc_call_nature'].empty_label = "--Select--"
        self.fields['sc_call_purpose'].empty_label = "--Select--"

        # Populate sc_joint_call_name with choices from the related MyUser model
        self.fields['sc_joint_call_name'].queryset = MyUser.objects.all()
