from django.db import models

from .customerdepartment_mod import CustomerdepartmentInfo
from .emailtype_mod import Email_type
from ..models import Tr_triptype_Info,CustomerInfo, MyUser


class Emailmaster(models.Model):
    em_Customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, default='')
    em_to_names = models.TextField(blank=True, null=True, help_text="Comma-separated email list")
    em_cc_names = models.TextField(blank=True, null=True, help_text="Comma-separated email list")
    em_emailtype = models.ForeignKey(Email_type, on_delete=models.CASCADE, null=True,blank=True)
    em_customerdepartment = models.ForeignKey(CustomerdepartmentInfo, on_delete=models.CASCADE, default='',blank=True, null=True)
    em_user = models.CharField(max_length=255, blank=True, null=True, verbose_name="User")
    em_updated_at = models.DateTimeField(null=True, auto_now=True)
    em_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    class Meta:
        ordering = ["em_Customer_name"]

    def __str__(self):
        return self.em_Customer_name
