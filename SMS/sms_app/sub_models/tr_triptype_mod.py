from django.db import models

class Tr_triptype_Info(models.Model):
    tr_trip_type = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["tr_trip_type"]

    def __str__(self):
        return self.tr_trip_type