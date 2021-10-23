from django.db import models


# Create your models here.

class Post(models.Model):
	text = models.TextField(default=None, null=True)
	image = models.ImageField(upload_to='post/images', default=None, null=True)
	date_created = models.DateTimeField(auto_now_add=True)
	poster = models.ForeignKey('Account.User', on_delete=models.CASCADE)
