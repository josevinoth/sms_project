from django.db import models
from ..models import Prod_Type
class Product_info(models.Model):
    prod_name = models.CharField(max_length=100)
    #prod_manufacturer = models.CharField(max_length=50)
    prod_description = models.CharField(max_length=50, default='')
    # prod_category = models.ForeignKey(Prod_Cat, on_delete=models.CASCADE, default='')
    prod_type = models.ForeignKey(Prod_Type, on_delete=models.CASCADE, default='')

    def __str__(self):
        return self.prod_name