from django.db import models
from ..models import task_Info,MyUser

class timesheet_Info(models.Model):
    ts_task_id = models.ForeignKey(task_Info, on_delete=models.CASCADE, related_name='ts_task_id',db_column='ts_task_id',default=5)
    ts_start_date = models.DateTimeField()
    ts_end_date = models.DateTimeField()
    ts_hours = models.FloatField(default=0.0)
    ts_hours_test = models.FloatField(default=0.0)
    ts_developer = models.ForeignKey(MyUser, on_delete=models.CASCADE,related_name='ts_developer', db_column='ts_developer')
    ts_remarks = models.TextField(max_length=30, blank=True, null=True)
    ts_updated_at = models.DateTimeField(null=True, auto_now=True)
    ts_updated_by = models.ForeignKey(MyUser, related_name='ts_updated_by', db_column='ts_updated_by',
                                     on_delete=models.CASCADE, null=True)
    class Meta:
        ordering = ["ts_task_id"]

    def __str__(self):
        return self.ts_task_id