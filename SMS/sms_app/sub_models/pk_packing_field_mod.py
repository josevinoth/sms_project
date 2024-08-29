from django.db import models

class Napackingfield(models.Model):
    packing_field = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["packing_field"]

    def __str__(self):
        return self.packing_field