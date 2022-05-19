from django.db import models
from ..models import StatusList

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
    full_name = models.CharField(max_length=100)
    location = models.CharField(max_length=10, choices=LOCATION_CHOICE, default='')
    designation = models.CharField(max_length=10, choices=DESIGNATION_CHOICE, default='')
    email = models.CharField(max_length=10)
    contact = models.CharField(max_length=10)
    employee_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default='')
    role = models.CharField(max_length=10, choices=ROLE_CHOICE, default='User')