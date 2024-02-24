from django.db import models

class Busnotwon(models.Model):
    bus_notwon_reason = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["bus_notwon_reason"]

    def __str__(self):
        return self.bus_notwon_reason