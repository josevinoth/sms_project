from django.db import models
from ..models import CustomerInfo,CustomerdepartmentInfo,MyUser,VehiclecategoryInfo,VehicletypeInfo,StatusList,City

class EnquirynoteInfo(models.Model):
    en_enquirynumber = models.CharField(max_length=10,default = '')
    en_customername = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, default='')
    en_othercustomer = models.CharField(max_length=10,default = '')
    en_customercode = models.CharField(max_length=10,default = '')
    en_customerdepartment = models.ForeignKey(CustomerdepartmentInfo, on_delete=models.CASCADE, default='')
    en_customercontact = models.CharField(max_length=30)
    en_customeremail = models.CharField(max_length=30)
    en_raisedon = models.CharField(max_length=30)
    en_vehiclecategory = models.ForeignKey(VehiclecategoryInfo,on_delete=models.CASCADE, default='')
    en_vehicletype = models.ForeignKey(VehicletypeInfo,on_delete=models.CASCADE, default='')
    en_assignedto = models.ForeignKey(MyUser,on_delete=models.CASCADE, default='')
    en_status = models.ForeignKey(StatusList,on_delete=models.CASCADE, default='')
    en_fromlocaion = models.ForeignKey(City,on_delete=models.CASCADE,related_name='en_fromlocaion', db_column='en_fromlocaion')
    en_tolocation = models.ForeignKey(City,on_delete=models.CASCADE,related_name='en_tolocation', db_column='en_tolocation')
    en_raisedby =  models.CharField(max_length=30)
    en_lastmodifiedby = models.CharField(max_length=30)



    def __str__(self):
        return self.en_enquirynumber