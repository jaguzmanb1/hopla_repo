from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone

# Create your models here.
class User(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)

    REQUIRED_FIELDS = ['name', "password"]
    USERNAME_FIELD = 'email'

    def check_password(self, p_password): 
        return p_password == self.password

class Ticket(models.Model):
    id = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    images_count = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)

class Image(models.Model):
    id = models.AutoField(primary_key=True)
    id_ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    url = models.CharField(max_length=400)
