from django.db import models

class Tour_type(models.Model):
    tour_type = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["tour_type"]

    def __str__(self):
        return self.tour_type