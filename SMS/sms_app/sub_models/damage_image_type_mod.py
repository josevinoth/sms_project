from django.db import models
from ..models import Country,State

class damage_image_type_info(models.Model):
    dimt_name = models.CharField(max_length=100, default='')


    class Meta:
        ordering = ["dimt_name"]

    def __str__(self):
        return self.dimt_name