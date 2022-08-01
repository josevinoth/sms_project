from django.db import models
class UploadInfo(models.Model):
    file_upload_nam=models.FileField(upload_to='documents/%Y/%m/%d/')
    image_upload_nam=models.ImageField(upload_to='documents/%Y/%m/%d/')
    upload_description = models.CharField(max_length=100, null=True,default='')
    #
    # def __str__(self):
    #     return self.bo_body