from django.db import models

class pk_itemInfo(models.Model):
    item_name = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["item_name"]

    def __str__(self):
        return self.item_name