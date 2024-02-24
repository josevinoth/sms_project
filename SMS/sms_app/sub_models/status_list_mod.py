from django.db import models

class StatusList(models.Model):
    status_title = models.CharField(max_length=100, null=True)

    class Meta:
        ordering = ["status_title"]

    def __str__(self):
        return self.status_title