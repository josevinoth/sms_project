from django.db import models

class Natypeofwood(models.Model):
    type_of_wood = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["type_of_wood"]

    def __str__(self):
        return self.type_of_wood