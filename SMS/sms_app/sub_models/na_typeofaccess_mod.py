from django.db import models

class Natypeofaccess(models.Model):
    type_of_access = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["type_of_access"]

    def __str__(self):
        return self.type_of_access