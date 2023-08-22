from django.db import models

class Source(models.Model):
    source = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["source"]

    def __str__(self):
        return self.source