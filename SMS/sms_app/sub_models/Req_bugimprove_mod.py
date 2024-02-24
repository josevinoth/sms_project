from django.db import models

class Reqbugimprove(models.Model):
    rq_bugimprove = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["rq_bugimprove"]

    def __str__(self):
        return self.rq_bugimprove