from django.db import models

class StatusListManager(models.Manager):
    def get_queryset(self):
        # Exclude "Cancellation with Billing" (9) and "Cancellation without Billing" (10)
        return super().get_queryset().exclude(id__in=[9, 10])

class StatusList(models.Model):
    status_title = models.CharField(max_length=100, null=True)

    objects = StatusListManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ["status_title"]

    def __str__(self):
        return self.status_title