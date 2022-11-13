from django.db import models
class Stock_type(models.Model):
    stock_type = models.CharField(max_length=50, null=True)

    class Meta:
        ordering = ["stock_type"]
    def __str__(self):
        return self.stock_type