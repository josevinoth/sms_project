from django.db import models
from ..models import MyUser,Reqbugimprove,StatusList,Reqmodule

def requirements_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'Req_Files/{0}/{1}'.format(instance.req_number, filename)
class RequirementsInfo(models.Model):
    req_number = models.CharField(max_length=100,null=True,blank=True, default='')
    req_backlogs = models.TextField(max_length=500, default='')
    req_module = models.ForeignKey(Reqmodule, on_delete=models.CASCADE, default='')
    req_phase = models.CharField(max_length=100, default=1)
    req_owner = models.ForeignKey(MyUser, on_delete=models.CASCADE,related_name='req_owner', db_column='req_owner', default='')
    req_bugimprove = models.ForeignKey(Reqbugimprove, on_delete=models.CASCADE, default='')
    req_implementedby = models.ForeignKey(MyUser, on_delete=models.CASCADE,related_name='req_implementedby', db_column='req_implementedby', null=True,blank=True)
    req_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=2,null=True)
    req_remarks = models.TextField(max_length=500, default='',blank=True, null=True)
    req_raisedon = models.DateField(null=True,blank=True)
    req_implementedon = models.DateField(null=True,blank=True)
    req_created_at = models.DateTimeField(null=True, auto_now_add=True)
    req_updated_at = models.DateTimeField(null=True, auto_now=True)
    req_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    req_attachment = models.FileField(upload_to=requirements_directory_path, null=True, blank=True)
    class Meta:
        ordering = ["req_number"]

    def __str__(self):
        return self.req_number