import profile
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from .models import Profile


class UserTestCase(TestCase):
  def setUp(self):
    user = User.objects.create(username='test1', password='password')
    user.set_password('password')
    user.save()

  def test_user_password_is_hashed(self):
    user = User.objects.get(username='test1')
    self.assertNotEqual(user.password, 'password')
    
  def test_unique_username_is_enforced(self):
    with self.assertRaises(IntegrityError):
      User.objects.create(username='test1')
      
class ProfileTestCase(TestCase):
  def setUp(self):
    user = User.objects.create(username='test1', password='password')
    Profile.objects.create(user=user)
    
  def test_profile_default_balance_is_0(self):
    user = User.objects.get(username='test1')
    profile = Profile.objects.get(user=user)
    self.assertEqual(profile.balance, 0.00)
    