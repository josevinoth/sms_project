from django import forms
from ..models import ml_Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = ml_Product
        # fields = ['name', 'categories']
        fields = '__all__'
        widgets = {
            'categories': forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'id_categories'}),
        }
