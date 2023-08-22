from django.db import models

class Natypeofplywood(models.Model):
    type_of_plywood = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["type_of_plywood"]

    def __str__(self):
        return self.type_of_plywood