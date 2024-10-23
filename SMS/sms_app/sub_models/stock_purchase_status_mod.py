from django.db import models
class PkstockpurchaseStatus(models.Model):
    stockpurchasestatus = models.CharField(max_length=100, null=True)

    class Meta:
        ordering = ["stockpurchasestatus"]
    def __str__(self):
        return self.stockpurchasestatus