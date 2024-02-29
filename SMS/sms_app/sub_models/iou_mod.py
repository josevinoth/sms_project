from django.db import models
from ..models import User,ExpenseCategoryInfo,MyUser,Business_Sol_info
from django.urls import reverse

class iou_info(models.Model):
    staff_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_id', to_field='username',db_column='staff_id')
    staff_name = models.CharField(max_length=255,null=True,blank=True)
    transaction_type = models.ForeignKey(ExpenseCategoryInfo, on_delete=models.CASCADE)
    transaction_date = models.DateField()
    business_type = models.ForeignKey(Business_Sol_info, on_delete=models.CASCADE)
    amount=models.FloatField(default=0.0)
    iou_created_at = models.DateTimeField(null=True, auto_now_add=True)
    iou_updated_at = models.DateTimeField(null=True, auto_now=True)
    iou_updated_by = models.ForeignKey(MyUser, null=True,blank=True,on_delete=models.CASCADE, related_name='iou_updated_by',db_column='iou_updated_by',)
    iou_number=models.CharField(max_length=20,null=True,blank=True)


    class Meta:
        ordering = ["iou_number"]

    def __str__(self):
        return self.iou_number

    def get_absolute_url_iou(self):
        return reverse('iou_update', args=[str(self.id)])