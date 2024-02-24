from django.db import models

class Prod_Cat(models.Model):
    prod_cat_title = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.prod_cat_title