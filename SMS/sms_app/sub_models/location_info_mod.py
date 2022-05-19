from django.db import models
from ..models import Country,State,City,StatusList

class Location_info(models.Model):
    loc_name = models.CharField(max_length=100)
    loc_country = models.ForeignKey(Country, on_delete=models.CASCADE, default='')
    loc_state = models.ForeignKey(State, on_delete=models.CASCADE, default='')
    loc_city = models.ForeignKey(City, on_delete=models.CASCADE, default='')
    loc_zipcode = models.CharField(max_length=10)
    loc_address = models.CharField(max_length=300)
    loc_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default='')

    def __str__(self):
        return self.loc_name