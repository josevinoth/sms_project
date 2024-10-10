from django import forms
from ..models import CameraImage

class cameraForm(forms.ModelForm):
    class Meta:
        model = CameraImage
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(cameraForm,self).__init__(*args, **kwargs)
        self.fields['requirement_id'].empty_label = "--Select--"
