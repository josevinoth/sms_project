from django import forms
from ..models import Ar_comments_Info

class ArCommentsaddForm(forms.ModelForm):
    class Meta:
        model = Ar_comments_Info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ArCommentsaddForm,self).__init__(*args, **kwargs)
        self.fields['arc_customer'].empty_label = "--Select--"