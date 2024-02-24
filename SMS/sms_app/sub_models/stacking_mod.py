from django.db import models

class StackingInfo(models.Model):
    stack_layer = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["stack_layer"]

    def __str__(self):
        return self.stack_layer