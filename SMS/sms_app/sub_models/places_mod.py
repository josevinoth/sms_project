from django.db import models
from ..models import City
from django.urls import reverse

class Places(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, default='')
    place_name = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["place_name"]

    def __str__(self):
        return self.place_name

    def get_absolute_url(self):
        return reverse('places_update', args=[str(self.id)])