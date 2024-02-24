from django.db import models
from ..models import Country,State

class Fumigation_ActionInfo(models.Model):
    action_taken_by = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["action_taken_by"]

    def __str__(self):
        return self.action_taken_by