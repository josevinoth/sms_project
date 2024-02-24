from django.db import models

class Callnature(models.Model):
    call_nature = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["call_nature"]
    def __str__(self):
        return self.call_nature