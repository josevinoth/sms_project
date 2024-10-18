from django.db import models
from ..models import damage_image_type_info,DamagereportInfo
class PictureImage(models.Model):
    pi_reference = models.ForeignKey(DamagereportInfo,on_delete=models.CASCADE)
    pi_image_type = models.ForeignKey(damage_image_type_info,on_delete=models.CASCADE)
    pi_image = models.ImageField(upload_to='picture/', blank=True, null=True)

    def __str__(self):
        return f"Image taken at {self.pi_reference}"