from django.db import models
from ..models import applicaiton_Info,MyUser

class timesheet_Info(models.Model):
    ts_application = models.ForeignKey(applicaiton_Info, on_delete=models.CASCADE, related_name='ts_application',db_column='ts_application')
    ts_main_task = models.CharField(max_length=100)
    ts_sub_task = models.CharField(max_length=100)
    ts_start_date = models.DateTimeField()
    ts_end_date = models.DateTimeField()
    ts_hours = models.FloatField(default=0.0)
    ts_developer = models.ForeignKey(MyUser, on_delete=models.CASCADE,related_name='ts_developer', db_column='ts_developer')
    ts_remarks = models.TextField(max_length=30, blank=True, null=True)

    class Meta:
        ordering = ["ts_application"]

    def __str__(self):
        return self.ts_application