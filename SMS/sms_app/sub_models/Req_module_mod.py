from django.db import models

class Reqmodule(models.Model):
    rq_module = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["rq_module"]

    def __str__(self):
        return self.rq_module