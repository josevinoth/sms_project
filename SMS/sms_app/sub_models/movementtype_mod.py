from django.db import models
class MovementtypeInfo(models.Model):
    mt_movementtype = models.CharField(max_length=100, null=True,default='')

    # def __str__(self):
    #     return self.role_name