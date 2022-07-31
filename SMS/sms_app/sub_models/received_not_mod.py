from django.db import models
class Received_not(models.Model):
    received_not_name = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["received_not_name"]

    def __str__(self):
        return self.received_not_name