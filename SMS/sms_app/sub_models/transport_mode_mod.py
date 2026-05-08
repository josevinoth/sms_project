from django.db import models

class Transport_mode(models.Model):
    transport_mode = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["transport_mode"]

    def __str__(self):
        return self.transport_mode