from django.db import models
from ..models import applicaiton_Info

class task_Info(models.Model):
    application = models.ForeignKey(applicaiton_Info,on_delete=models.CASCADE, related_name='application',db_column='application',default=1)
    main_task = models.CharField(max_length=100)
    sub_task = models.CharField(max_length=100)
    remarks = models.TextField(max_length=30, blank=True, null=True)

    class Meta:
        ordering = ["main_task"]

    def __str__(self):
        return self.main_task