from django.db import models

class Calltype(models.Model):
    call_type = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["call_type"]

    def __str__(self):
        return self.call_type