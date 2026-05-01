from django.db import models
from .my_user_mod import MyUser
from .vendor_info_mod import Vendor_info
from .unit_info_mod import UnitInfo

class PkToolMaster(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('In Use', 'In Use'),
        ('Under Repair', 'Under Repair'),
        ('Scrap', 'Scrap'),
    ]
    USAGE_CHOICES = [
        ('Daily', 'Daily'),
        ('Project based', 'Project based'),
    ]

    tm_tool_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    tm_location = models.ForeignKey(UnitInfo, on_delete=models.SET_NULL, null=True, blank=True)
    tm_name = models.CharField(max_length=255)
    tm_size = models.CharField(max_length=100, null=True, blank=True)
    tm_brand = models.CharField(max_length=100, null=True, blank=True)
    tm_model_no = models.CharField(max_length=100, null=True, blank=True)
    tm_serial_no = models.CharField(max_length=100, unique=True)
    tm_purchase_date = models.DateField(null=True, blank=True)
    tm_vendor = models.ForeignKey(Vendor_info, on_delete=models.SET_NULL, null=True, blank=True)
    tm_invoice_no = models.CharField(max_length=100, null=True, blank=True)
    tm_invoice_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tm_warranty_expiry = models.DateField(null=True, blank=True)
    tm_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Available')
    tm_usage_type = models.CharField(max_length=50, choices=USAGE_CHOICES, default='Project based')
    tm_bill_attachment = models.FileField(upload_to='tools/bills/', null=True, blank=True)
    tm_image = models.ImageField(upload_to='tools/images/', null=True, blank=True)
    
    tm_created_at = models.DateTimeField(auto_now_add=True)
    tm_updated_at = models.DateTimeField(auto_now=True)
    tm_updated_by = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Tool Master"
        verbose_name_plural = "Tool Master"
        ordering = ['tm_name']

    def __str__(self):
        return f"{self.tm_name} - {self.tm_serial_no}"
