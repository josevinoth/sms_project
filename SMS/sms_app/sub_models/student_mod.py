from django.db import models


class Stud_reg(models.Model):
    stud_name = models.CharField(max_length=100, default='')
    stud_age = models.IntegerField(default='')
    stud_eng = models.IntegerField(default='')
    stud_tamil = models.IntegerField(default='')
    stud_math = models.IntegerField(default='')
    stud_social = models.IntegerField(default='')
    stud_science = models.IntegerField(default='')