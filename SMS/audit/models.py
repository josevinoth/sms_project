from django.db import models
from django.contrib.auth.models import User

class SystemAuditLog(models.Model):
    ACTION_CHOICES = (
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    )

    module_name = models.CharField(max_length=100, db_index=True)
    model_name = models.CharField(max_length=100, db_index=True)
    record_id = models.CharField(max_length=255, db_index=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    changed_data = models.JSONField(null=True, blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.module_name} - {self.model_name} ({self.record_id}) - {self.action}"
