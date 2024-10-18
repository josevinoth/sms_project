from django.db import models
class PkstockpurchaseStatus(models.Model):
    pk_stockpurchasestatus = models.CharField(max_length=50, null=True)

    class Meta:
        ordering = ["pk_stockpurchasestatus"]
    def __str__(self):
        return self.pk_stockpurchasestatus