from django.db import models
class Stock_type_maintenance(models.Model):
    stock_type_maintenance = models.CharField(max_length=50, null=True)

    class Meta:
        ordering = ["stock_type_maintenance"]
    def __str__(self):
        return self.stock_type_maintenance