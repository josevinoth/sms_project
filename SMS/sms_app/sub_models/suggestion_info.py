from django.db import models
from ..models import User_extInfo

class suggestioninfo(models.Model):
    raised_by = models.ForeignKey(User_extInfo, on_delete=models.CASCADE, null=True, blank=True,related_name='raised_by',db_column='raised_by')
    request = models.TextField(null=True, blank=True)
    suggestion_by = models.ForeignKey(User_extInfo, on_delete=models.CASCADE, null=True, blank=True,related_name='suggestion_by',db_column='suggestion_by')
    suggestion = models.TextField(null=True, blank=True)
    query_created_at = models.DateTimeField(null=True, auto_now_add=True)
    query_updated_at = models.DateTimeField(null=True, auto_now=True)
    def __str__(self):
        return self.request