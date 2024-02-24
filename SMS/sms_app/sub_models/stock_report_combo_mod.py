from django.db import models
from ..models import Location_info,UnitInfo

class Stock_report_combo(models.Model):
    WH_Job_Number = models.CharField(max_length=100, default='')
    Stock_number = models.CharField(max_length=100, default='')
    Customer = models.CharField(max_length=100, default='')
    Arrival_Date = models.CharField(max_length=100, default='')
    Loading_Time = models.CharField(max_length=100, default='')
    Unloading_Time = models.CharField(max_length=100, default='')
    Transporter = models.CharField(max_length=100, default='')
    Truck_Number = models.CharField(max_length=100, default='')
    Consignee = models.CharField(max_length=100, default='')
    Consigner = models.CharField(max_length=100, default='')
    DOCS_Received = models.CharField(max_length=100, default='')
    HAWB = models.CharField(max_length=100, default='')
    Destination = models.CharField(max_length=100, default='')
    Customer_Invoice = models.CharField(max_length=100, default='')
    Checkin_Weight = models.CharField(max_length=100, default='')
    Checkin_Qty = models.CharField(max_length=100, default='')
    Package_Type = models.CharField(max_length=100, default='')
    Invoice_Weight = models.CharField(max_length=100, default='')
    Invoice_Qty = models.CharField(max_length=100, default='')
    Length = models.CharField(max_length=100, default='')
    Width = models.CharField(max_length=100, default='')
    Height = models.CharField(max_length=100, default='')
    Volume_Weight = models.CharField(max_length=100, default='')
    CBM = models.CharField(max_length=100, default='')
    Currency_Type = models.CharField(max_length=100, default='')
    Invoice_Value = models.CharField(max_length=100, default='')
    Invoice_Value_INR = models.CharField(max_length=100, default='')
    E_Way_Bill = models.CharField(max_length=100, default='')
    Fumigation_Date = models.CharField(max_length=100, default='')
    Branch = models.CharField(max_length=100, default='')
    Unit = models.CharField(max_length=100, default='')
    bay = models.CharField(max_length=100, default='')
    Checked_In_Out = models.CharField(max_length=100, default='')
    Storage_Days = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["WH_Job_Number"]

    def __str__(self):
        return self.WH_Job_Number