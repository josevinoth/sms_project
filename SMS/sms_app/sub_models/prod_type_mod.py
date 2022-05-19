from django.db import models
class Prod_Type(models.Model):
    prod_type_title = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.prod_type_title