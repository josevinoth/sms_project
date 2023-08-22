from django.db import models

class Nawoodnorms(models.Model):
    wood_norms = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["wood_norms"]

    def __str__(self):
        return self.wood_norms