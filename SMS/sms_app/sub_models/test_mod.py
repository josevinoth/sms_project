from django.db import models
from ..models import Location_info,UnitInfo

class testnfo(models.Model):
    test_bayname = models.CharField(max_length=100, default='')
    test_branch_name = models.ForeignKey(Location_info,on_delete=models.CASCADE,default='')
    test_unit_name = models.ForeignKey(UnitInfo,on_delete=models.CASCADE,default='')

    class Meta:
        ordering = ["test_bayname"]

    def __str__(self):
        return self.test_bayname