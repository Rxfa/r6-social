from email.policy import default
from django.contrib.auth.models import User
from django.db import models
from django_countries.fields import CountryField

# Create your models here.

REGION_CHOICES = [
  ('EU', 'EUROPE'),
  ('NA', 'NORTH AMERICA'),
  ('LATAM', 'LATIN AMERICA'),
  ('APAC', 'ASIA-PACIFIC'),
  ('INT', 'INTERNATIONAL'),
]

class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  bio = models.TextField(blank=True, null=True)
  balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
  country = CountryField()
  profile_pic = models.ImageField(blank=True, null=True, upload_to='profiles/')
  fav_team = models.CharField(blank=True, null=True)
  

class Competition(models.Model):
  
  TYPE_CHOICES = [
    ('LAN'),
    ('Online')
  ]
  
  TIER_CHOICES = [
    ('S', 'S-Tier'),
    ('A', 'A-Tier'),
    ('B', 'B-Tier'),
    ('C', 'C-Tier'),
    ('D', 'D-Tier')
  ]
  
  id = models.PositiveSmallIntegerField(primary_key=True)
  year = models.PositiveSmallIntegerField()
  name = models.CharField()
  type = models.CharField(max_length=1, choices=TYPE_CHOICES)
  logo = models.ImageField(default='default/no_image.jpg', upload_to='competitions/logos/')
  region = models.CharField(max_length=1, choices=REGION_CHOICES)
  tier = models.CharField(max_length=1, choices=TIER_CHOICES)
  current_matchday = models.PositiveSmallIntegerField()
  n_of_matchdays = models.PositiveSmallIntegerField()
  n_of_teams = models.PositiveSmallIntegerField()
  n_of_games = models.PositiveSmallIntegerField()
  last_updated = models.DateField
  
  class Meta:
    ordering = ['-year', 'name']
    get_latest_by = 'last_updated'

  def __str__(self):
    return f'{self.name} - matchday {self.current_matchday}'


class Table(models.Model):
  competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
  
  def __str__(self):
    return f'{self.competition} Table'
  
class Standing(models.Model):
  table = models.ForeignKey(Table, on_delete=models.CASCADE)
  position = models.PositiveSmallIntegerField()
  played_games = models.PositiveSmallIntegerField()
  points = models.PositiveSmallIntegerField()
  wins = models.PositiveSmallIntegerField()
  overtime_wins = models.PositiveSmallIntegerField()
  overtime_losses = models.PositiveSmallIntegerField()
  losses = models.PositiveSmallIntegerField()
  round_difference = models.PositiveSmallIntegerField()
  
  class Meta:
    ordering = ['position']
  