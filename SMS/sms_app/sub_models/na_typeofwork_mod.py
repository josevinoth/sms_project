from django.db import models

class Natypeofwork(models.Model):
    type_of_work = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["type_of_work"]

    def __str__(self):
        return self.type_of_work