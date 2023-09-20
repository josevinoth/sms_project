from django.db import models
class Pkstocktype(models.Model):
    pk_stocktype = models.CharField(max_length=50, null=True)

    class Meta:
        ordering = ["pk_stocktype"]
    def __str__(self):
        return self.pk_stocktype