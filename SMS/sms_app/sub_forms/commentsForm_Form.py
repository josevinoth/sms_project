from django import forms
from ..models import commentsInfo

class commentsaddForm(forms.ModelForm):
    class Meta:
        model = commentsInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(commentsaddForm,self).__init__(*args, **kwargs)
        self.fields['comments_updated_by'].empty_label = "--Select--"