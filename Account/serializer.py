from django.contrib.auth import authenticate, login
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from Account.models import User


class BasicUserSerializer(ModelSerializer):
	'''
		This serializer is used to return few details of the user
	'''
	class Meta:
		model = User
		fields = ('id', 'username')


class UserSerializer(ModelSerializer):
	'''
		This serializer is used to return a user's full details
	'''
	followers = serializers.ListSerializer(child=BasicUserSerializer(), read_only=True)
	following = serializers.SerializerMethodField('following_', read_only=True)
	no_of_followers = serializers.SerializerMethodField('followers_count', read_only=True)
	no_of_following = serializers.SerializerMethodField('following_count', read_only=True)
	no_of_posts = serializers.SerializerMethodField('posts_count', read_only=True)

	class Meta:
		model = User
		fields = ('id', 'first_name', 'last_name', 'username', 'is_active', 'no_of_posts', 'no_of_followers', 'no_of_following',
				  'followers', 'following')

	def following_(self, obj):
		return BasicUserSerializer(obj.following(), many=True).data

	def followers_count(self, obj):
		return obj.followers_count()

	def following_count(self, obj):
		return obj.following_count()

	def posts_count(self, obj):
		return obj.posts_count()


class SignupSerializer(ModelSerializer):
	'''
		This serializer validates and executes user signup process
	'''
	first_name = serializers.CharField(required=True)
	last_name = serializers.CharField(required=True)
	email = serializers.EmailField(required=True)
	password_1 = serializers.CharField(min_length=8, allow_null=False, required=True)
	password_2 = serializers.CharField(min_length=8, allow_null=False, required=True)

	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'username', 'email', 'password_1', 'password_2')

	def validate(self, initial_data):
		if User.objects.filter(username=str(initial_data['username']).lower()).exists():
			raise Exception('A user with this username already exists')
		if User.objects.filter(email=str(initial_data['email']).lower()).exists():
			raise Exception('A user with this email already exists')
		if initial_data['password_1'] != initial_data['password_2']:
			raise Exception('The two passwords are not equal')
		else:
			initial_data['password'] = initial_data['password_1']
			del initial_data['password_1'], initial_data['password_2']
		return initial_data

	def create(self, validated_data):
		user = User.objects.create_user(**validated_data)
		return user


class LoginSerializer(ModelSerializer):
	'''
		This user validates and executes user's login process
	'''
	username = serializers.CharField(allow_null=False, required=True)
	password = serializers.CharField(allow_null=False, required=True)

	class Meta:
		model = User
		fields = ('username', 'password')

	def validate(self, initial_data):
		user = authenticate(username=initial_data['username'], password=initial_data['password'])
		if user is None:
			raise Exception('Wrong credentials. Please kindly check your login credentials')
		initial_data['user'] = user
		return initial_data

	def login(self, request):
		obj = TokenObtainPairSerializer()
		user = self.validated_data['user']
		del self.validated_data['user']
		token = obj.validate(dict(**self.validated_data))
		login(request, user)
		user_data = UserSerializer(user).data
		user_data['token'] = token
		return user_data


class UpdateUserDetailsSerializer(ModelSerializer):
	'''
		This serializer validates and executes the process of updating a user's details
	'''
	username = serializers.CharField(min_length=3, allow_null=False, required=False)
	email = serializers.EmailField(required=False)
	first_name = serializers.CharField(required=False)
	last_name = serializers.CharField(required=False)

	class Meta:
		model = User
		fields = ('username', 'email', 'first_name', 'last_name')

	def validate(self, initial_data):
		if 'username' in initial_data:
			if User.objects.filter(username=str(initial_data['username']).lower()).exists():
				raise Exception('A user with this username already exists')
		if 'email' in initial_data:
			if User.objects.filter(email=str(initial_data['email']).lower()).exists():
				raise Exception('A user with this email already exists')
		return initial_data

	def update(self, instance, validated_data):
		User.objects.filter(pk=instance.pk).update(**validated_data)
		instance.refresh_from_db()
		return instance

	def execute(self):
		return UserSerializer(self.update(self.instance, self.validated_data)).data


class UserActionSerializer(Serializer):
	'''
		This serializer validates and executes the follow and unfollow process
	'''
	action = serializers.ChoiceField(choices=['follow', 'unfollow'], required=True)

	def update(self, instance, validated_data):
		pass

	def create(self, validated_data):
		pass

	def validate(self, initial_data):
		if not User.objects.filter(id=self.context['followee']).exists():
			raise Exception(f'No User exists with this ID "{self.context["followee"]}"')
		self.context['followee'] = User.objects.get(id=self.context['followee'])
		if self.context['followee'] == self.instance:
			raise Exception('You cannot follow or unfollow yourself')
		if initial_data['action'] == 'follow' and self.context['followee'].followers.filter(
				id=self.instance.id).exists():
			raise Exception('You are already following this user')
		elif initial_data['action'] == 'unfollow' and not self.context['followee'].followers.filter(
				id=self.instance.id).exists():
			raise Exception('You are not following this user')
		elif initial_data['action'] not in ('follow', 'unfollow'):
			raise Exception('Wrong action')
		return initial_data

	def execute(self):
		followee = self.context['followee']
		followee.followers.add(self.instance) if self.validated_data[
															'action'] == 'follow' else followee.followers.remove(
			self.instance)
		followee.save()
		message = f'You just {self.validated_data["action"]}ed {self.context["followee"].username} successfully'
		return {"message": message, "data": UserSerializer(self.instance).data}
