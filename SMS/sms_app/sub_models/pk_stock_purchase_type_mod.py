from django.db import models
class Pkstockpurchasetype(models.Model):
    pk_stockpurchasetype = models.CharField(max_length=50, null=True)

    class Meta:
        ordering = ["pk_stockpurchasetype"]
    def __str__(self):
        return self.pk_stockpurchasetype