from django.db import models
from .part_code_mod import PkpartcodeInfo
from .stock_type_mod import Stock_type
from .stocktype_maintenance_mod import Stock_type_maintenance
from .unit_of_measure_mod import Unitofmeasure

class StockMaintenance(models.Model):
    sm_stock_type = models.ForeignKey(Stock_type_maintenance, on_delete=models.CASCADE, null=True, blank=True)
    sm_invoice_date = models.DateField(null=True, blank=True)
    sm_invoice_no = models.CharField(max_length=100, null=True, blank=True)
    sm_partcode = models.ForeignKey(PkpartcodeInfo, on_delete=models.CASCADE, null=True, blank=True)
    
    # Auto-filled fields
    sm_description = models.CharField(max_length=255, null=True, blank=True)
    sm_thickness = models.FloatField(default=0.0, null=True, blank=True)
    sm_width = models.FloatField(default=0.0, null=True, blank=True)
    sm_length = models.FloatField(default=0.0, null=True, blank=True)
    sm_uom = models.ForeignKey(Unitofmeasure, on_delete=models.SET_NULL, null=True, blank=True)
    
    sm_count = models.IntegerField(default=0, null=True, blank=True)
    sm_cft = models.FloatField(default=0.0, null=True, blank=True)
    sm_total_cft = models.FloatField(default=0.0, null=True, blank=True)
    sm_per_unit_cost = models.FloatField(default=0.0, null=True, blank=True)
    
    # "total wood price(cal by total cft * 100" (or similar, per user prompt)
    sm_total_wood_price = models.FloatField(default=0.0, null=True, blank=True)
    
    sm_created_at = models.DateTimeField(auto_now_add=True, null=True)
    sm_updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.sm_invoice_no} - {self.sm_partcode}"
