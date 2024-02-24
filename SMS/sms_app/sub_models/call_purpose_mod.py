from django.db import models

class Callpurpose(models.Model):
    call_purpose = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["call_purpose"]

    def __str__(self):
        return self.call_purpose