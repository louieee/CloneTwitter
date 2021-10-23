from django.core.cache import cache
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status, viewsets

# Create your views here.
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from Post.models import Post
from Post.serializer import PostSerializer, AddPostSerializer
from Utilities.api_response import api_exception, APISuccess, choice_query, image_upload, APIFailure, CACHE_TTL


class ReadListDeletePost(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
	permission_classes = (IsAuthenticated, )
	queryset = Post.objects.all()
	serializer_class = PostSerializer

	def get_queryset(self):
		choice = self.request.query_params.get('choice', 'all')
		if choice == 'mine':
			queryset = cache.get(f'mine_posts_{self.request.user.id}', None)
			if queryset is None:
				queryset = Post.objects.filter(poster=self.request.user)
				cache.set(f'mine_posts_{self.request.user.id}', queryset, timeout=CACHE_TTL)
		elif choice == 'followers':
			queryset = cache.get(f'followers_posts_{self.request.user.id}', None)
			if queryset is None:
				queryset = Post.objects.filter(poster__in=self.request.user.followers)
				cache.set(f'followers_posts_{self.request.user.id}', queryset, timeout=CACHE_TTL)
		elif choice == 'following':
			queryset = cache.get(f'following_posts_{self.request.user.id}', None)
			if queryset is None:
				queryset = Post.objects.filter(poster__in=self.request.user.following())
				cache.set(f'following_posts_{self.request.user.id}', queryset, timeout=CACHE_TTL)
		elif choice == 'all':
			queryset = cache.get(f'all_posts_{self.request.user.id}', None)
			if queryset is None:
				queryset = Post.objects.all()
				cache.set(f'all_posts_{self.request.user.id}', queryset, timeout=CACHE_TTL)
		else:
			return APIFailure(message="Please Enter a valid choice", status=status.HTTP_400_BAD_REQUEST)
		return queryset

	@swagger_auto_schema(manual_parameters=[choice_query])
	@api_exception
	def list(self, request, *args, **kwargs):
		return mixins.ListModelMixin.list(self, request, *args, **kwargs)

	@api_exception
	def retrieve(self, request, *args, **kwargs):
		return mixins.RetrieveModelMixin.retrieve(self, request, *args, **kwargs)

	@api_exception
	def destroy(self, request, *args, **kwargs):
		return mixins.DestroyModelMixin.destroy(self, request, *args, **kwargs)


class CreatePost(mixins.CreateModelMixin, viewsets.GenericViewSet):
	permission_classes = (IsAuthenticated,)
	queryset = Post.objects.all()
	serializer_class = AddPostSerializer
	parser_classes = (MultiPartParser,)

	@swagger_auto_schema(manual_parameters=[image_upload])
	@api_exception
	def create(self, request, *args, **kwargs):
		serializer = self.serializer_class(data=request.data)
		serializer.context['user'] = request.data
		serializer.context['image'] = request.FILES['image']
		serializer.is_valid(raise_exception=True)
		post = serializer.save()
		data = PostSerializer(post).data
		return APISuccess(message='You have just added a post', data=data)


class EditPost(mixins.UpdateModelMixin, viewsets.GenericViewSet):
	permission_classes = (IsAuthenticated,)
	queryset = Post.objects.all()
	serializer_class = AddPostSerializer
	http_method_names = ('patch', )
	parser_classes = (MultiPartParser,)

	@swagger_auto_schema(manual_parameters=[image_upload])
	@api_exception
	def partial_update(self, request, *args, **kwargs):
		serializer = self.serializer_class(data=request.data, partial=True)
		serializer.context['user'] = request.data
		serializer.is_valid(raise_exception=True)
		post = serializer.save()
		data = PostSerializer(post).data
		return APISuccess(message='You have just added a post', data=data)