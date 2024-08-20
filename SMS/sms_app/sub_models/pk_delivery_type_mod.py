from django.db import models

class Nadeliverytype(models.Model):
    delivery_type = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["delivery_type"]

    def __str__(self):
        return self.delivery_type