from django.db import models
class Currency_type(models.Model):
    currency_type = models.CharField(max_length=50, null=True)
    converision_value = models.FloatField(null=True,default=0.0)

    class Meta:
        ordering = ["currency_type"]

    def __str__(self):
        return self.currency_type