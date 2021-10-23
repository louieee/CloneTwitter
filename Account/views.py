from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins, status
# Create your views here.
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from Account.models import User
from Account.serializer import SignupSerializer, BasicUserSerializer, LoginSerializer, UpdateUserDetailsSerializer, \
	UserSerializer, UserActionSerializer
from Utilities.api_response import api_exception, APISuccess, user_id


class Signup(mixins.CreateModelMixin, viewsets.GenericViewSet):
	queryset = User.objects.all()
	serializer_class = SignupSerializer
	parser_classes = (MultiPartParser,)

	@api_exception
	def create(self, request, *args, **kwargs):
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = BasicUserSerializer(serializer.save()).data
		return APISuccess(message='Signup successful', data=user, status=status.HTTP_201_CREATED)


class Login(APIView):
	parser_classes = (MultiPartParser,)
	http_method_names = ('post', )

	@swagger_auto_schema(request_body=LoginSerializer)
	@api_exception
	def post(self, request, *args, **kwargs):
		serializer = LoginSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.login(request)
		return APISuccess(message='Login successful', data=data)


class EditUser(APIView):
	parser_classes = (MultiPartParser,)
	permission_classes = (IsAuthenticated, )
	http_method_names = ('patch',)

	@swagger_auto_schema(request_body=UpdateUserDetailsSerializer)
	@api_exception
	def patch(self, request, *args, **kwargs):
		serializer = UpdateUserDetailsSerializer(data=request.data, instance=request.user, partial=True)
		serializer.is_valid(raise_exception=True)
		data = serializer.execute()
		return APISuccess(message='User Detail Updated Successfully', data=data)


class ActionUser(APIView):
	parser_classes = (MultiPartParser,)
	permission_classes = (IsAuthenticated,)
	http_method_names = ('post', )

	@swagger_auto_schema(request_body=UserActionSerializer, manual_parameters=[user_id])
	@api_exception
	def post(self, request, *args, **kwargs):
		serializer = UserActionSerializer(data=request.data, instance=request.user)
		serializer.context['followee'] = kwargs['id']
		serializer.is_valid(raise_exception=True)
		data = serializer.execute()
		return APISuccess(**data)


class UserProfile(APIView):
	permission_classes = (IsAuthenticated,)
	http_method_names = ('get',)

	@api_exception
	def get(self, request, *args, **kwargs):
		serializer = UserSerializer(instance=request.user)
		return APISuccess(message='user profile retrieved', data=serializer.data)