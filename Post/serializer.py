from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from rest_framework.views import APIView

from Account.serializer import BasicUserSerializer
from Post.models import Post


class PostSerializer(ModelSerializer):
	poster = BasicUserSerializer(read_only=True)

	class Meta:
		model = Post
		fields = "__all__"


class AddPostSerializer(ModelSerializer):
	text = serializers.CharField(required=False)

	class Meta:
		model = Post
		fields = ('text',)

	def validate(self, initial_data):
		text = initial_data.get('text', None)
		image = self.context.get('image', None)
		if text is None and image is None:
			raise Exception('Query cannot be empty')
		if Post.objects.filter(text=text, image=image).exists():
			raise Exception('Duplicate data')
		initial_data['poster'] = self.context['user']
		return initial_data

	def create(self, validated_data):
		post = Post.objects.create(**validated_data)
		return post

	def update(self, instance, validated_data):
		Post.objects.filter(pk=instance.pk).update(**validated_data)
		instance.refresh_from_db()
		return instance


