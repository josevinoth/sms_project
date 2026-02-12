from django.db import models

class Complaint_type(models.Model):
    complaint_type = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["complaint_type"]

    def __str__(self):
        return self.complaint_type