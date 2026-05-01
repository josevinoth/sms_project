from django.db import models
from .my_user_mod import MyUser

class DeletionLog(models.Model):
    dl_model_name = models.CharField(max_length=100)
    dl_record_id = models.IntegerField()
    dl_record_identifier = models.CharField(max_length=255, blank=True, null=True) # e.g. Enquiry Number
    dl_deleted_by = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True)
    dl_deleted_at = models.DateTimeField(auto_now_add=True)
    dl_reason = models.TextField()

    class Meta:
        ordering = ["-dl_deleted_at"]

    def __str__(self):
        return f"{self.dl_model_name} {self.dl_record_id} deleted by {self.dl_deleted_by}"
