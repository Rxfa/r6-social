from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  balance = models.DecimalField(..., max_digits=12, decimal_places=2)
  profile_pic = models.ImageField(blank=True, null=True, upload_to='assets/profiles/')
  bio = models.TextField(blank=True, null=True)