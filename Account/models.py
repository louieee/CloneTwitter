from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from rest_framework_simplejwt.tokens import RefreshToken


class User(AbstractUser):
	followers = models.ManyToManyField('User', related_name='userfollowers')

	def following(self):
		return User.objects.filter(followers__username=self.username)

	def followers_count(self):
		return self.followers.count()

	def following_count(self):
		return self.following().count()

	def tokens(self):
		refresh = RefreshToken.for_user(self)
		return {
			'refresh': str(refresh),
			'access': str(refresh.access_token)
		}


