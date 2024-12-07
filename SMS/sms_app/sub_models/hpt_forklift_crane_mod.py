from django.db import models

class hptforkliftcraneInfo(models.Model):
    hpt_forklift_crane_name = models.CharField(max_length=20,default = '')

    class Meta:
        ordering = ["hpt_forklift_crane_name"]

    def __str__(self):
        return self.hpt_forklift_crane_name