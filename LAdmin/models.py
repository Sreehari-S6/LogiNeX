from django.db import models
from homeapp.models import tbl_login,tbl_user
# Create your models here.
class tbl_routes(models.Model):
    departure_port = models.EmailField(max_length=350)
    arrival_port = models.CharField(max_length=358)

    def __str__(self):
        return f"{self.departure_port} → {self.arrival_port}"