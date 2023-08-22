from django.db import models

class Naconsumables(models.Model):
    consumables = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["consumables"]

    def __str__(self):
        return self.consumables