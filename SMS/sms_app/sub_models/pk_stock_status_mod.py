from django.db import models


class pk_stock_statusinfo(models.Model):
    status_name = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["status_name"]

    def __str__(self):
        return self.status_name
