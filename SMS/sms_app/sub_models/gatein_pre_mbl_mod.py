from django.db import models
from ..models import StatusList,Location_info

def gateinpre_shipment_mbl_attach_path(instance, filename):
    return 'gpmattachfiles/{0}/{1}'.format(instance.gpm_shipment_details, filename)
def gateinpre_customer_mbl_attach_path(instance, filename):
    return 'gpmattachfiles/{0}/{1}'.format(instance.gpm_customer_approval, filename)
class gateinpre_mblInfo(models.Model):
    gpm_branch = models.ForeignKey(Location_info, on_delete=models.CASCADE, default='')
    gpm_shipment_details = models.FileField(upload_to=gateinpre_shipment_mbl_attach_path, null=True, blank=True)
    gpm_customer_approval = models.FileField(upload_to=gateinpre_customer_mbl_attach_path, null=True, blank=True)
    gpm_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default='')

    class Meta:
        ordering = ["gpm_branch"]
    def __str__(self):
        return self.gpm_branch