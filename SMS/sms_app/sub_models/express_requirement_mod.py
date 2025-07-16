from django.db import models

class Expressrequirementinfo(models.Model):
    express_requirement = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["express_requirement"]

    def __str__(self):
        return self.express_requirement