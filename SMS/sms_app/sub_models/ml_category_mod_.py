from django.db import models
from ..models import Product_info
class ml_Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ml_Product(models.Model):
    name = models.CharField(max_length=100)
    categories = models.ManyToManyField(Product_info)  # Multi-select field

    def __str__(self):
        return self.name
