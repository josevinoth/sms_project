from django.db import models
from ..models import damage_image_type_info,DamagereportInfo


def picture_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    image_type_name = instance.pi_image_type
    filename = f"{image_type_name}_{instance.pi_reference.id}.{ext}"
    return f"DamagereportPictures/{instance.pi_reference}/{filename}"

class PictureImage(models.Model):
    pi_reference = models.ForeignKey(DamagereportInfo,on_delete=models.CASCADE)
    pi_image_type = models.ForeignKey(damage_image_type_info,on_delete=models.CASCADE)
    pi_image = models.ImageField(upload_to=picture_upload_path, blank=True, null=True)
    pi_timestamp = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return f"Image taken at {self.pi_reference}"