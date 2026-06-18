from django.db import models
from homeapp.models import tbl_login,tbl_user,tbl_company
from LAdmin.models import tbl_routes
class tbl_ship(models.Model):
    ship_id = models.AutoField(primary_key=True)
    ship_name = models.CharField(max_length=100)
    company_id = models.ForeignKey(
        tbl_company,
        on_delete=models.CASCADE
    )
    capacity_ton = models.IntegerField()
    built_year = models.IntegerField()
    image = models.ImageField(upload_to='ships/')
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.ship_name
    
class tbl_company_ship_route(models.Model):
    ship_route_id = models.AutoField(primary_key=True)
    ship_id = models.ForeignKey(tbl_ship, on_delete=models.CASCADE)
    route_id = models.ForeignKey(tbl_routes, on_delete=models.CASCADE)
    start_date = models.DateField()
    arrival_date = models.DateField()
    status = models.CharField(max_length=50, default="Active")

    def __str__(self):
        # ✅ MUST return STRING ONLY
        return f"{self.ship_id.ship_name} → {self.route_id}"


class tbl_feedbacks(models.Model):

    feedback_id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=150)

    email = models.EmailField()

    contact_no = models.CharField(max_length=20)

    message = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.email}"