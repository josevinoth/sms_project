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
    
    # External Customer Links
    linked_customer = models.ForeignKey('CustomerInfo', on_delete=models.SET_NULL, null=True, blank=True)
    is_lp_customer = models.BooleanField(default=False)
    
    # Registration Approval Status
    is_approved = models.BooleanField(default=True)

    # Customer Portal Role & Plant Assignment
    PORTAL_ROLE_CHOICES = (
        ('STANDARD', 'Standard Customer'),
        ('PARENT', 'Parent / 3PL Account (e.g. Expo Freight)'),
        ('FACTORY', 'Child Factory / Inplant (e.g. Brandix Plant)'),
        ('LOGISTICS', 'Child Central Logistics Officer (e.g. Brandix Logistics)'),
    )
    portal_role = models.CharField(max_length=20, choices=PORTAL_ROLE_CHOICES, default='STANDARD')
    agent_account = models.CharField(max_length=150, null=True, blank=True, help_text="e.g. Brandix (when acting as an Agent/Sub-Account under a Parent Customer like Expo Freight)")
    assigned_plant = models.CharField(max_length=100, null=True, blank=True, help_text="e.g. Brandix B1, B2, etc.")


    def __str__(self):
        return self.user.username