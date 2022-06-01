from django.db import models
from ..models import StatusList

class Department_info(models.Model):
    dept_name = models.CharField(max_length=100)
    dept_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default='')
    def __str__(self):
        return self.dept_name