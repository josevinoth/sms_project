from django.db import models
from ..models import RequirementsInfo,MyUser,applicaiton_Info

class task_Info(models.Model):
    application = models.ForeignKey(applicaiton_Info,on_delete=models.CASCADE, related_name='application',db_column='application',default=1)
    main_task = models.CharField(max_length=100)
    sub_task = models.CharField(max_length=100)
    remarks = models.TextField(max_length=30, blank=True, null=True)
    task_id = models.CharField(max_length=100,blank=True,null=True)
    t_updated_at = models.DateTimeField(null=True, auto_now=True)
    t_updated_by = models.ForeignKey(MyUser, related_name='t_updated_by', db_column='t_updated_by',on_delete=models.CASCADE, null=True)
    t_requirement_id = models.ForeignKey(RequirementsInfo, related_name='t_requirement_id', db_column='t_requirement_id',on_delete=models.CASCADE,null=True,blank=True)
    t_requirement_description = models.TextField(max_length=500, blank=True, null=True)
    class Meta:
        ordering = ["task_id"]

    def __str__(self):
        return self.task_id