from django.db import models

class GoodnotgoodInfo(models.Model):
    Goodnotgood_name = models.CharField(max_length=20,default = '')

    class Meta:
        ordering = ["Goodnotgood_name"]

    def __str__(self):
        return self.Goodnotgood_name