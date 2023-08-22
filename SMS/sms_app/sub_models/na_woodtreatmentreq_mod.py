from django.db import models

class Nawoodtreatmentreq(models.Model):
    wood_treatment_req = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["wood_treatment_req"]

    def __str__(self):
        return self.wood_treatment_req