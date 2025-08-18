from django.db import models

class Cross_labelling_info(models.Model):
    cross_labelling_name = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["cross_labelling_name"]

    def __str__(self):
        return self.cross_labelling_name