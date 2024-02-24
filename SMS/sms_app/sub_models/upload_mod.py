from django.db import models
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'UploadInfo/{0}/{1}'.format(instance.upload_description, filename)
class UploadInfo(models.Model):
    file_upload_nam=models.FileField(upload_to=user_directory_path)
    image_upload_nam=models.ImageField(upload_to=user_directory_path)
    upload_description = models.CharField(max_length=100, null=True,default='')

    # class Meta:
    #     db_table = "uploadInfo"
    #
    # def __str__(self):
    #     return self.bo_body