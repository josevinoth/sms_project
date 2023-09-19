from django.contrib.auth.models import User
from django.db import models
from ..models import RoleInfo,Location_info,DesignationInfo,Business_Sol_info,Department_info

class User_extInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    department = models.ForeignKey(Department_info, on_delete=models.CASCADE, null=True,blank=True)
    emp_contact = models.CharField(max_length=10,null=True,blank=True)
    emp_designation = models.ForeignKey(DesignationInfo, on_delete=models.CASCADE, null=True,blank=True)
    emp_branch = models.ForeignKey(Location_info, on_delete=models.CASCADE, null=True,blank=True)
    emp_role = models.ForeignKey(RoleInfo, on_delete=models.CASCADE, null=True,blank=True)
    emp_pan = models.CharField(max_length=100,null=True,blank=True)
    emp_uan = models.CharField(max_length=100,null=True,blank=True)
    emp_esi = models.CharField(max_length=100,null=True,blank=True)
    emp_aadhar = models.CharField(max_length=100,null=True,blank=True)
    emp_DOB = models.CharField(max_length=100, null=True,blank=True)
    emp_DOJ = models.CharField(max_length=100, null=True,blank=True)
    emp_organisation = models.ForeignKey(Business_Sol_info, on_delete=models.CASCADE, null=True,blank=True)


    def __str__(self):
        return self.user.username