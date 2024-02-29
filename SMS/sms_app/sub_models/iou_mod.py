from django.db import models
from ..models import ExpenseCategoryInfo,MyUser,Business_Sol_info
from django.urls import reverse

class iuo_info(models.Model):
    staff_name = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='staff_name',db_column='staff_name',)
    transaction_type = models.ForeignKey(ExpenseCategoryInfo, on_delete=models.CASCADE)
    transaction_date = models.DateField()
    business_type = models.ForeignKey(Business_Sol_info, on_delete=models.CASCADE)
    amount=models.FloatField(default=0.0)
    iou_created_at = models.DateTimeField(null=True, auto_now_add=True)
    iou_updated_at = models.DateTimeField(null=True, auto_now=True)
    iou_updated_by = models.ForeignKey(MyUser, null=True,blank=True,on_delete=models.CASCADE, related_name='iou_updated_by',db_column='iou_updated_by',)


    class Meta:
        ordering = ["staff_name"]

    def __str__(self):
        return self.staff_name

    def get_absolute_url_iou(self):
        return reverse('iou_update', args=[str(self.id)])