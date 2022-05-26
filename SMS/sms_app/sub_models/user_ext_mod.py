from django.contrib.auth.models import User
from django.db import models

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
    department = models.CharField(max_length=100,null=True)
    emp_contact = models.CharField(max_length=10,null=True)
    emp_designation = models.CharField(max_length=10, choices=DESIGNATION_CHOICE, null=True)
    emp_branch = models.CharField(max_length=10, choices=LOCATION_CHOICE, null=True)
    emp_role = models.CharField(max_length=10, choices=ROLE_CHOICE,null=True)

    def __str__(self):
        return self.user.username