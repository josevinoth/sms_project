from django.db import models

class Naplywoodthickness(models.Model):
    plywood_thickness = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["plywood_thickness"]

    def __str__(self):
        return self.plywood_thickness