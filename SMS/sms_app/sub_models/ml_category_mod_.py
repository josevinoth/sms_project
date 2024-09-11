from django.db import models

class ml_Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ml_Product(models.Model):
    name = models.CharField(max_length=100)
    categories = models.ManyToManyField(ml_Category)  # Multi-select field

    def __str__(self):
        return self.name
