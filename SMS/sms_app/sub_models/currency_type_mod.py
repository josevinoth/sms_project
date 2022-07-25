from django.db import models
class Currency_type(models.Model):
    currency_type = models.CharField(max_length=50, null=True)

    class Meta:
        ordering = ["currency_type"]

    def __str__(self):
        return self.currency_type