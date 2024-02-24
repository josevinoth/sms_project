from django.db import models

class Natypeofreq(models.Model):
    type_of_req = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["type_of_req"]

    def __str__(self):
        return self.type_of_req