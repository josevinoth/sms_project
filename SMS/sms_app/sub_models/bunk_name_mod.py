from django.db import models

class Bunkname(models.Model):
    bunk_name = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["bunk_name"]

    def __str__(self):
        return self.bunk_name