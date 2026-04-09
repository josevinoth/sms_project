from django.db import models

class Travel_type(models.Model):
    travel_type = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["travel_type"]

    def __str__(self):
        return self.travel_type