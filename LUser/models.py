from django.db import models
from django.db import models
from homeapp.models import tbl_login, tbl_user, tbl_company
from LAdmin.models import tbl_routes
from LCompany.models import tbl_ship
from django.utils import timezone

class tbl_transportation_request(models.Model):
    request_id = models.AutoField(primary_key=True)

    user_id = models.ForeignKey(
        tbl_user,
        on_delete=models.CASCADE
    )

    route_id = models.ForeignKey(
        tbl_routes,
        on_delete=models.CASCADE
    )

    company_id = models.ForeignKey(
        tbl_company,
        on_delete=models.CASCADE
    )

    ship_id = models.ForeignKey(
        tbl_ship,
        on_delete=models.CASCADE
    )

    container_type = models.CharField(max_length=200)

    weight_ton = models.FloatField()

    pickup_address = models.TextField()

    delivery_address = models.TextField()

    status = models.CharField(
        max_length=50,
        default="Pending"
    )

    requested_at = models.DateTimeField(
        auto_now_add=True
    )

    amount = models.CharField(
    max_length=20,
    null=True,
    blank=True,
    default=None
    )


    def __str__(self):
        # MUST return string only
        return f"Request {self.request_id} - {self.user_id}"

class tbl_payment(models.Model):

    payment_id = models.AutoField(primary_key=True)

    date = models.DateTimeField(default=timezone.now)

    request_id = models.ForeignKey(
        'tbl_transportation_request',
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"Payment {self.payment_id} - {self.amount}"
    
class tbl_address(models.Model):
    # 1. Define the choices constant
    ADDRESS_TYPE_CHOICES = [
        ('Home', 'Home Address'),
        ('Company', 'Company Address'),
        ('Other', 'Other'),
    ]

    address_id = models.AutoField(primary_key=True)

    # 2. Apply choices to the field
    type = models.CharField(
        max_length=50, 
        choices=ADDRESS_TYPE_CHOICES,
        default='Home'
    )

    place = models.CharField(max_length=250)

    city = models.CharField(max_length=200)

    district = models.CharField(max_length=200)

    state = models.CharField(max_length=200)

    pincode = models.CharField(max_length=10)

    user_id = models.ForeignKey(
        tbl_user,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.place}, {self.city} ({self.type})"
    
class tbl_review(models.Model):

    review_id = models.AutoField(primary_key=True)

    date = models.DateTimeField(
        default=timezone.now
    )

    user_id = models.ForeignKey(
        tbl_user,
        on_delete=models.CASCADE
    )

    request_id = models.ForeignKey(
        'tbl_transportation_request',
        on_delete=models.CASCADE
    )

    comment = models.TextField()

    def __str__(self):
        return f"Review {self.review_id} - {self.user_id}"    