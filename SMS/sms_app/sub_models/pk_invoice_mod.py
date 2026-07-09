from django.db import models
from ..models import (
    PkneedassessmentInfo, PkpurchaseorderInfo, CustomerInfo, MyUser, POdimension
)


class PkInvoice(models.Model):
    """
    PMS Invoice — Master record.
    One invoice per job/PO, created BEFORE Gate Pass is issued.
    """
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Partial', 'Partial'),
        ('Paid', 'Paid'),
    ]

    inv_number = models.CharField(max_length=50, unique=True, verbose_name="Invoice Number")
    inv_job_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="Job No")
    inv_assessment_num = models.ForeignKey(
        PkneedassessmentInfo, on_delete=models.CASCADE,
        blank=True, null=True, verbose_name="Assessment"
    )
    inv_customer_po = models.ForeignKey(
        PkpurchaseorderInfo, on_delete=models.CASCADE,
        blank=True, null=True, verbose_name="Customer PO"
    )
    inv_customer_name = models.ForeignKey(
        CustomerInfo, on_delete=models.CASCADE,
        blank=True, null=True, verbose_name="Customer"
    )
    inv_date = models.DateField(verbose_name="Invoice Date")
    inv_base_amount = models.FloatField(default=0.0, verbose_name="Base Amount (₹)")
    inv_gst_rate = models.FloatField(default=18.0, verbose_name="GST Rate (%)")
    inv_cgst_amount = models.FloatField(default=0.0, verbose_name="CGST (₹)")
    inv_sgst_amount = models.FloatField(default=0.0, verbose_name="SGST (₹)")
    inv_igst_amount = models.FloatField(default=0.0, verbose_name="IGST (₹)")
    inv_total_amount = models.FloatField(default=0.0, verbose_name="Grand Total (₹)")
    inv_remarks = models.TextField(blank=True, null=True, verbose_name="Remarks")
    inv_payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES,
        default='Pending', verbose_name="Payment Status"
    )
    inv_created_by = models.ForeignKey(
        MyUser, on_delete=models.SET_NULL, null=True,
        related_name='pk_invoices_created', verbose_name="Created By"
    )
    inv_created_at = models.DateTimeField(auto_now_add=True)
    inv_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.inv_number


class PkInvoiceItem(models.Model):
    """
    PMS Invoice Line Item — one row per PO Dimension (box/pallet).
    Linked to a POdimension record which carries the item number.
    """
    inv_master = models.ForeignKey(
        PkInvoice, on_delete=models.CASCADE,
        related_name='items', verbose_name="Invoice"
    )
    inv_pod_dimension = models.ForeignKey(
        POdimension, on_delete=models.PROTECT,
        blank=True, null=True, verbose_name="PO Dimension"
    )
    # Snapshot fields — copied from POdimension at invoice creation time
    inv_item_number = models.CharField(max_length=150, verbose_name="Item Number")
    inv_description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Description")
    inv_length = models.FloatField(default=0.0, verbose_name="Length")
    inv_width = models.FloatField(default=0.0, verbose_name="Width")
    inv_height = models.FloatField(default=0.0, verbose_name="Height")
    inv_uom = models.CharField(max_length=20, blank=True, null=True, verbose_name="UOM")
    inv_qty = models.IntegerField(default=1, verbose_name="Qty")
    inv_unit_value = models.FloatField(default=0.0, verbose_name="Unit Value (₹)")
    inv_total_value = models.FloatField(default=0.0, verbose_name="Total Value (₹)")

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.inv_master.inv_number} — {self.inv_item_number}"
