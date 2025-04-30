from django.db import models

from SMS.sms_app.sub_models.pk_stock_type_mod import Pkstocktype

class Pkwooddescription(models.Model):
    pk_wood_description = models.CharField(max_length=50, null=True)
    pk_na_stock_type = models.ForeignKey(Pkstocktype,on_delete=models.CASCADE,default='')

    class Meta:
        ordering = ["pk_wood_description"]
    def __str__(self):
        return self.pk_wood_description