from django.db import models

class Costtype(models.Model):
    cost_type = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["cost_type"]

    def __str__(self):
        return self.cost_type