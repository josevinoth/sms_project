from django.db import models
from ..models import Country,State

class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, default='')
    state = models.ForeignKey(State, on_delete=models.CASCADE, default='')
    city_name = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["city_name"]

    def __str__(self):
        return self.city_name