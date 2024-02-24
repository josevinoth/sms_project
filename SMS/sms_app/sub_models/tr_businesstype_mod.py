from django.db import models

class Tr_businesstype_Info(models.Model):
    tr_business = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["tr_business"]

    def __str__(self):
        return self.tr_business