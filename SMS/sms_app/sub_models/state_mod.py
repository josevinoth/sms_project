from django.db import models
from ..models import Country

class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, default='')
    state_name = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.state_name