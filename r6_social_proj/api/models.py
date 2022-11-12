from django.contrib.auth.models import User
from django.db import models
from django_countries.fields import CountryField


class Team(models.Model):
  id = models.PositiveSmallIntegerField(primary_key=True)
  logo = models.ImageField(default='default/no_image.jpg', upload_to='teams/logos/')
  name = models.CharField(max_length=30)
  short_name = models.CharField(null=True, blank=True, max_length=3)
  class Meta:
    ordering = ['name']
    
  def __str__(self):
    return self.name


class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  bio = models.TextField(blank=True, null=True)
  balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
  country = CountryField()
  profile_pic = models.ImageField(blank=True, null=True, upload_to='profiles/')
  fav_team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.CASCADE)

  
class Player(models.Model):
  team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.CASCADE)
  nickname = models.CharField(max_length=30)
  name = models.CharField(max_length=30)
  nationality = CountryField()
  image = models.ImageField(blank=True, null=True, default='default/no_image.jpg', upload_to='players/images/')
  
  class Meta:
    ordering = ['team', 'name']
    
  def __str__(self):
    return f'{self.nickname}.{self.team.short_name}'
