from django.db import models

class CameraImage(models.Model):
    image = models.ImageField(upload_to='camera_images/')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image taken at {self.timestamp}"