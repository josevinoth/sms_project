from django.db import models
class Wh_chargetype(models.Model):
    charge_Type = models.CharField(max_length=100, null=True,default='')

    class Meta:
        ordering = ["charge_Type"]

    def __str__(self):
        return self.charge_Type