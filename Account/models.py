from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from rest_framework_simplejwt.tokens import RefreshToken


class User(AbstractUser):
	followers = models.ManyToManyField('User', related_name='userfollowers')

	def following(self):
		'''
			The queryset for users that this user is following
		:return:
		'''
		return User.objects.filter(followers__username=self.username)

	def followers_count(self):
		'''
			The number of users following this user
		:return:
		'''
		return self.followers.count()

	def following_count(self):
		'''
			The number of users this user is following
		:return:
		'''
		return self.following().count()

	def tokens(self):
		'''
			This is the auth token for this user
		:return:
		'''
		refresh = RefreshToken.for_user(self)
		return {
			'refresh': str(refresh),
			'access': str(refresh.access_token)
		}

	def posts_count(self):
		'''
			This is the number of posts this user has
		:return:
		'''
		from Post.models import Post
		return Post.objects.filter(poster=self).count()


