from django.db import models
from ..models import MyUser,Reqbugimprove,StatusList,Reqmodule

class RequirementsInfo(models.Model):
    req_number = models.CharField(max_length=100, default='')
    req_backlogs = models.TextField(max_length=500, default='')
    req_module = models.ForeignKey(Reqmodule, on_delete=models.CASCADE, default='')
    req_phase = models.CharField(max_length=100, default=1)
    req_owner = models.ForeignKey(MyUser, on_delete=models.CASCADE,related_name='req_owner', db_column='req_owner', default='')
    req_bugimprove = models.ForeignKey(Reqbugimprove, on_delete=models.CASCADE, default='')
    req_implementedby = models.ForeignKey(MyUser, on_delete=models.CASCADE,related_name='req_implementedby', db_column='req_implementedby', null=True,blank=True)
    req_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=6,null=True)
    req_remarks = models.TextField(max_length=500, default='',blank=True, null=True)
    req_raisedon = models.DateTimeField(null=True,blank=True)
    req_implementedon = models.DateField(null=True,blank=True)
    req_created_at = models.DateTimeField(null=True, auto_now_add=True)
    req_updated_at = models.DateTimeField(null=True, auto_now=True)
    req_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ["req_number"]

    def __str__(self):
        return self.req_number