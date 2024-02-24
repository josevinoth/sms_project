from django.db import models

class Naitemname(models.Model):
    item_name = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["item_name"]

    def __str__(self):
        return self.item_name