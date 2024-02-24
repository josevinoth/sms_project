from django.db import models

class Unitofmeasure(models.Model):
    unit_of_measure = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["unit_of_measure"]

    def __str__(self):
        return self.unit_of_measure