from django.db import models
from django.contrib.auth.models import User

class UserPageAccess(models.Model):
    """
    Stores granular page and module access rights granted to a user.
    Supports View, Create, Edit, Delete CRUD permissions.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='page_access_set')
    page_key = models.CharField(max_length=120, db_index=True)
    can_view = models.BooleanField(default=True)
    can_create = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    granted_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='granted_page_access_set')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sms_user_page_access'
        unique_together = ('user', 'page_key')
        indexes = [
            models.Index(fields=['user', 'page_key']),
        ]
        verbose_name = 'User Page Access'
        verbose_name_plural = 'User Page Accesses'

    def __str__(self):
        return f"{self.user.username} - {self.page_key}"
