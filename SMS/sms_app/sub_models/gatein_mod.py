from django.db import models
from ..models import MyUser,StatusList,VehicletypeInfo,CustomerInfo,TrbusinesstypeInfo,CustomerdepartmentInfo

class Gatein_info(models.Model):
    gatein_job_no = models.CharField(blank=False, null=False, max_length=20)
    gatein_invoice = models.CharField(blank=False, null=False,max_length=20)
    gatein_customer = models.ForeignKey(CustomerInfo,on_delete=models.CASCADE, default='')
    gatein_customer_type = models.ForeignKey(TrbusinesstypeInfo,on_delete=models.CASCADE, default='')
    gatein_arrival_date = models.CharField(blank=True, null=True,max_length=20)
    gatein_department = models.ForeignKey(CustomerdepartmentInfo,on_delete=models.CASCADE, default='')
    gatein_shipper = models.CharField(blank=True, null=True, max_length=20)
    gatein_consignee = models.CharField(blank=True, null=True, max_length=20)
    gatein_no_of_pkg = models.IntegerField(blank=True, null=True)
    gatein_weight = models.IntegerField(blank=True, null=True)
    gatein_driver = models.CharField(blank=True, null=True, max_length=20)
    gatein_contact_number = models.CharField(blank=True, null=True, max_length=20)
    gatein_DL_number = models.CharField(blank=True, null=True, max_length=20)
    gatein_otl = models.CharField(blank=True, null=True, max_length=20)
    gatein_transporter = models.CharField(blank=True, null=True, max_length=100)
    gatein_truck_number = models.CharField(blank=True, null=True, max_length=20)
    gatein_truck_type = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, default='')
    gatein_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=6,null=True)
    gatein_created_at = models.DateTimeField(null=True,auto_now_add=True)
    gatein_updated_at = models.DateTimeField(null=True,auto_now=True)

