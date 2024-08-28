from django.db import models

class Nadimensiontype(models.Model):
    dimension_type = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["dimension_type"]

    def __str__(self):
        return self.dimension_type