from django.db import models
from ..models import Country,State,City,StatusList

class Vendor_info(models.Model):
    vend_name = models.CharField(max_length=100)
    vend_description = models.CharField(max_length=100, default='')
    vend_contact = models.CharField(max_length=10)
    vend_contact_per = models.CharField(max_length=50, default='')
    vend_gstin = models.CharField(max_length=10, default='')
    vend_designation = models.CharField(max_length=30)
    vend_email = models.CharField(max_length=50)
    vend_country = models.ForeignKey(Country, on_delete=models.CASCADE, default='')
    vend_state = models.ForeignKey(State, on_delete=models.CASCADE, default='')
    vend_city = models.ForeignKey(City, on_delete=models.CASCADE, default='')
    vend_zip = models.CharField(max_length=10)
    vend_address = models.CharField(max_length=300)
    vend_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default='')

    def __str__(self):
        return self.vend_name