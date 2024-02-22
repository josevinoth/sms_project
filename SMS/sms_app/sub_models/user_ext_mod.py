from django.contrib.auth.models import User
from django.db import models
from ..models import RoleInfo


class User_extInfo(models.Model):
    user_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    contact = models.CharField(max_length=10, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    role = models.ForeignKey(RoleInfo, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.user_name