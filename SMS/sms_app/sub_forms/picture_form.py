from django import forms
from ..models import PictureImage

class pictureForm(forms.ModelForm):
    class Meta:
        model = PictureImage
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(pictureForm,self).__init__(*args, **kwargs)
        self.fields['pi_image_type'].empty_label = "--Select--"
        self.fields['pi_reference'].empty_label = "--Select--"
