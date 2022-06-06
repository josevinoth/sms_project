from django.contrib.auth.models import User
from django.db import models
from ..models import RoleInfo,Location_info,DesignationInfo,Department_info

class User_extInfo(models.Model):
    STATUS_CHOICE = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('New User', 'New User')
    )

    DESIGNATION_CHOICE = (
        ('Director', 'Director'),
        ('Manager', 'Manager'),
        ('Supervisor', 'Supervisor'),
        ('Driver', 'Driver'),
        ('Helper', 'Helper')
    )
    LOCATION_CHOICE = (
        ('Chennai', 'Chennai'),
        ('Bangalore', 'Bangalore'),
        ('Hyderabad', 'Hyderabad')
    )
    ROLE_CHOICE = (
        ('Admin', 'Admin'),
        ('User', 'User')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    department = models.ForeignKey(Department_info, on_delete=models.CASCADE, null=True)
    emp_contact = models.CharField(max_length=10,null=True)
    emp_designation = models.ForeignKey(DesignationInfo, on_delete=models.CASCADE, null=True)
    emp_branch = models.ForeignKey(Location_info, on_delete=models.CASCADE, null=True)
    emp_role = models.ForeignKey(RoleInfo, on_delete=models.CASCADE, null=True)
    emp_pan = models.CharField(max_length=10,null=True,default='')
    emp_uan = models.CharField(max_length=10,null=True,default='')
    emp_esi = models.CharField(max_length=10,null=True,default='')
    emp_aadhar = models.CharField(max_length=10,null=True,default='')
    emp_DOB = models.CharField(max_length=10, null=True,default='')
    emp_DOJ = models.CharField(max_length=10, null=True,default='')


    def __str__(self):
        return self.user.username