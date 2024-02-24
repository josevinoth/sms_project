from django.db import models
from ..models import StatusList,Location_info

class Employee(models.Model):
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
    emp_empid=models.CharField(max_length=100,default='')
    emp_full_name = models.CharField(max_length=100,default='')
    emp_email = models.CharField(max_length=50, default='')
    emp_contact = models.CharField(max_length=10, default='')
    emp_designation = models.CharField(max_length=10, choices=DESIGNATION_CHOICE, default='')
    emp_branch = models.CharField(max_length=10, choices=LOCATION_CHOICE, default='User')
    emp_password = models.CharField(max_length=100, default='')
    emp_password_conf = models.CharField(max_length=100, default='')
    emp_role = models.CharField(max_length=10, choices=ROLE_CHOICE, default='User')
    emp_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default='')
