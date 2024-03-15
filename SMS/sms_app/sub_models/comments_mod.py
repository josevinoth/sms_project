from django.db import models
from ..models import MyUser

class commentsInfo(models.Model):
    comments_created_at = models.DateTimeField(null=True, auto_now_add=True)
    comments_updated_at = models.DateTimeField(null=True, auto_now=True)
    comments_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, related_name='comments_updated_by', db_column='comments_updated_by')
    comments_remarks = models.TextField(max_length=300, null=True, blank=True)
    comments_ref=models.CharField(max_length=50,null=True,blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.comments_remarks