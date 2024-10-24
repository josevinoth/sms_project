from django.db import models
from ..models import damage_image_type_info,DamagereportInfo
class CameraImage(models.Model):
    image = models.ImageField(upload_to='camera_images/')
    timestamp = models.DateTimeField(auto_now_add=True)
    reference = models.ForeignKey(DamagereportInfo,null=True,on_delete=models.CASCADE)
    image_type = models.ForeignKey(damage_image_type_info,null=True,on_delete=models.CASCADE)


    def __str__(self):
        return f"Image taken at {self.timestamp}"