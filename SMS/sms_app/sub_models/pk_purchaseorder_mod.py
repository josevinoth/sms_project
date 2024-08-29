import datetime

from django.db import models
from ..models import StatusList,PkquotationsummaryInfo,CustomerInfo,PkneedassessmentInfo,MyUser

def Pkpurchaseorder_directory_path(instance, filename):
    return 'Pkpurchaseorderfiles/{0}/{1}'.format(instance.po_num, filename)
class PkpurchaseorderInfo(models.Model):
    po_num = models.CharField(max_length=100)
    po_date = models.DateTimeField(blank=True, null=True)
    po_value = models.FloatField(blank=True, null=True, default=0.0)
    po_tax = models.FloatField(blank=True, null=True, default=0.0)
    po_total_value = models.FloatField(blank=True, null=True, default=0.0)
    po_validity_date = models.DateField(blank=True, null=True)
    po_payment_terms = models.CharField(max_length=30,null=True, blank=True)
    po_created_at = models.DateTimeField(null=True, auto_now_add=True)
    po_updated_at = models.DateTimeField(null=True, auto_now=True)
    po_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='po_updated_by',db_column='po_updated_by', null=True)
    po_assessment_num = models.ForeignKey(PkneedassessmentInfo, on_delete=models.CASCADE, related_name='po_assessment_num',db_column='po_assessment_num', blank=True,null=True)
    po_quotation_num = models.ForeignKey(PkquotationsummaryInfo, on_delete=models.CASCADE, related_name='po_quotation_num',db_column='po_quotation_num')
    po_customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, related_name='po_customer_name',db_column='po_customer_name', blank=True,null=True)
    po_attach = models.FileField(upload_to=Pkpurchaseorder_directory_path, null=True, blank=True)
    po_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, related_name='po_status',
                                  db_column='po_status', blank=True, null=True, default=6)
    po_comments_box = models.TextField(default="")
    class Meta:
        ordering = ["po_num"]

    def __str__(self):
        return self.po_num

    def save(self, *args, **kwargs):
        # Calculate total value: Value + (Value x Tax)
        self.po_total_value = self.po_value + (self.po_value * self.po_tax)
        super(PkpurchaseorderInfo, self).save(*args, **kwargs)