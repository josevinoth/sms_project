from django.db import models

class Branch(models.Model):
    branch = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["branch"]

    def __str__(self):
        return self.branch