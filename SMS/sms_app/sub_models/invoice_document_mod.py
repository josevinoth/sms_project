from django.db import models
from ..models import MyUser, Tripstatusinfo


def invoice_doc_path(instance, filename):
    return 'InvoiceDocuments/{0}/{1}'.format(instance.id_tripnumber, filename)


class InvoiceDocumentInfo(models.Model):
    id_tripnumber = models.CharField(max_length=300, null=True, blank=True)
    id_trip_cost_doc = models.FileField(upload_to=invoice_doc_path, null=True, blank=True)
    id_parking_doc = models.FileField(upload_to=invoice_doc_path, null=True, blank=True)
    id_toll_doc = models.FileField(upload_to=invoice_doc_path, null=True, blank=True)
    id_loading_doc = models.FileField(upload_to=invoice_doc_path, null=True, blank=True)
    id_unloading_doc = models.FileField(upload_to=invoice_doc_path, null=True, blank=True)
    id_weighment_doc = models.FileField(upload_to=invoice_doc_path, null=True, blank=True)
    id_handling_doc = models.FileField(upload_to=invoice_doc_path, null=True, blank=True)
    id_pod_doc = models.FileField(upload_to=invoice_doc_path, null=True, blank=True)
    id_merged_pdf = models.FileField(upload_to=invoice_doc_path, null=True, blank=True)
    id_status = models.ForeignKey(
        Tripstatusinfo, on_delete=models.SET_NULL, null=True, blank=True
    )
    id_created_at = models.DateTimeField(auto_now_add=True)
    id_updated_at = models.DateTimeField(auto_now=True)
    id_updated_by = models.ForeignKey(
        MyUser, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return str(self.id_tripnumber) if self.id_tripnumber else "N/A"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.id_status and self.id_tripnumber:
            from ..sub_models.tripdetail_mod import TripdetailInfo
            try:
                trip = TripdetailInfo.objects.get(tr_tripnumber=self.id_tripnumber)
                if trip.tc_financestatus != self.id_status:
                    trip.tc_financestatus = self.id_status
                    trip.save(update_fields=['tc_financestatus'])
            except TripdetailInfo.DoesNotExist:
                pass
