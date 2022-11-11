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
  
"""
class Competition(models.Model):
  
  REGION_CHOICES = [
    ('EU', 'EUROPE'),
    ('NA', 'NORTH AMERICA'),
    ('LATAM', 'LATIN AMERICA'),
    ('APAC', 'ASIA-PACIFIC'),
    ('INT', 'INTERNATIONAL'),
  ]
  
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
  type = models.CharField(max_length=30, choices=TYPE_CHOICES)
  logo = models.ImageField(default='default/no_image.jpg', upload_to='competitions/logos/')
  region = models.CharField(max_length=30, choices=REGION_CHOICES)
  tier = models.CharField(max_length=30, choices=TIER_CHOICES)
  current_matchday = models.PositiveSmallIntegerField()
  n_of_matchdays = models.PositiveSmallIntegerField()
  n_of_teams = models.PositiveSmallIntegerField()
  n_of_games = models.PositiveSmallIntegerField()
  last_updated = models.DateField
  
  class Meta:
    ordering = ['-year', 'name']
    get_latest_by = 'last_updated'
    abstract = True

  def __str__(self):
    return f'{self.name} - matchday {self.current_matchday}'


class Table(Competition):
  
  def __str__(self):
    return f'{self.name} Table'
  

class Standing(models.Model):
  table = models.ForeignKey(Table, on_delete=models.CASCADE)
  team = models.ForeignKey(Team, on_delete=models.CASCADE)
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
    
  def has_position_changed(self, previous_matchday_standing):
    return {
      self.played_games > previous_matchday_standing.played_games and
      self.position != previous_matchday_standing.position
    }
    
  def has_position_improved(self, previous_matchday_standing):
    return {
      self.played_games > previous_matchday_standing.played_games and
      self.position > previous_matchday_standing.position
    }
    

class Game(models.Model):
  MAPS = [
    ('Oregon', 'Oregon'),
    ('Chalet', 'Chalet'),
    ('Club House', 'Club House'),
    ('Bank', 'Bank'),
    ('Kafe Dostoyevsky', 'Kafe Dostoyevsky'),
    ('Villa', 'Villa'),
    ('Theme Park', 'Theme Park'),
    ('Border', 'Border'),
    ('Skyscraper', 'Skyscraper'),    
  ]
  team1 = models.ManyToManyField(Team)
  team2 = models.ManyToManyField(Team)
  score1 = models.PositiveSmallIntegerField()
  score2 = models.PositiveSmallIntegerField()
  map = models.CharField(max_length=1, choices=MAPS)

  def had_overtime(self):
    return self.score1 > 7 or self.score2 > 7
    
"""