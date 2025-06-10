from django.db import models

class approval_status_info(models.Model):
    approval_name = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["approval_name"]

    def __str__(self):
        return self.approval_name

