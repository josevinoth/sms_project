from django.db import models

from ..models import Pkstocktype


class Pkwooddescription(models.Model):
    pk_wood_type = models.ForeignKey(Pkstocktype, on_delete=models.CASCADE, null=True,related_name='pk_wood_type',
                                     db_column='pk_wood_type')
    pk_wood_description = models.CharField(max_length=50, null=True)

    class Meta:
        ordering = ["pk_wood_description"]
    def __str__(self):
        return self.pk_wood_description