from django.db import models

class Natypeofpack(models.Model):
    type_of_pack = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["type_of_pack"]

    def __str__(self):
        return self.type_of_pack