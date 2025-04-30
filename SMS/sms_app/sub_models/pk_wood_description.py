from django.db import models


class Pkwooddescription(models.Model):
    pk_wood_description = models.CharField(max_length=50, null=True)

    class Meta:
        ordering = ["pk_wood_description"]
    def __str__(self):
        return self.pk_wood_description