from django.db import models
from django.contrib.auth.models import User

class TransportMISMirrorSetting(models.Model):
    branch = models.CharField(max_length=100, default='All')
    year = models.IntegerField(default=2026)
    category_name = models.CharField(max_length=150)
    is_mirrored = models.BooleanField(default=False)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('branch', 'year', 'category_name')
        verbose_name = "Transport MIS Mirror Setting"
        verbose_name_plural = "Transport MIS Mirror Settings"

    def __str__(self):
        return f"{self.year} | {self.branch} | {self.category_name} | Mirrored={self.is_mirrored}"
