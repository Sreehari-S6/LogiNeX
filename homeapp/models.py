from django.db import models
from django.utils import timezone
# Create your models here.
class tbl_login(models.Model):
    email = models.EmailField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    usertype = models.CharField(max_length=10)

    def __str__(self):
        return self.email
class tbl_user(models.Model):
    name = models.CharField(max_length=150)
    login_id=models.ForeignKey(tbl_login, on_delete=models.CASCADE)
    phno = models.CharField(max_length=15)
    id_proof = models.CharField(max_length=256)
    country = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=50,default='active')

    def __str__(self):
        return f"{self.name}"
class tbl_company(models.Model):
    name = models.CharField(max_length=150)
    login_id=models.ForeignKey(tbl_login, on_delete=models.CASCADE)
    country = models.CharField(max_length=40)
    district = models.CharField(max_length=45)
    state = models.CharField(max_length=40)
    owner_name = models.CharField(max_length=40)
    licence = models.CharField(max_length=300)
    id_proof = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=50,default='active')

    def __str__(self):
        return f"{self.name}"    
   
class tbl_otp(models.Model):
    email = models.EmailField(max_length=150)
    otp = models.CharField(max_length=10)
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f"{self.email} - {self.otp}"    