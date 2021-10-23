from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from drf_yasg import openapi
from rest_framework import status
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

image_upload = openapi.Parameter(name="image", in_=openapi.IN_FORM, type=openapi.TYPE_FILE, required=False,
								 description="Supported images- ('jpg, png, jpeg, webp')")
choice_query = openapi.Parameter('choice', openapi.IN_QUERY,
								 description="options are : all, mine, followers, following",
								 type=openapi.TYPE_STRING)
user_id = openapi.Parameter(name='id', in_=openapi.IN_PATH, type=openapi.TYPE_NUMBER, required=True,
							description="This is the user's ID")

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

class APISuccess:
	def __new__(cls, message='Success', data=None, status=HTTP_200_OK):
		if data is None:
			data = dict()
		return Response({'status': "Success", 'message': message, 'data': data}, status)


class APIFailure:
	def __new__(cls, message='Error', status=HTTP_400_BAD_REQUEST):
		return Response({'status': 'Failed', 'message': message}, status)


def api_exception(func):
	def inner(self, request, *args, **kwargs):
		try:
			return func(self, request, *args, **kwargs)
		except Exception as e:
			error_msg = e.__str__().split('\n')[0]
			return APIFailure(message=error_msg, status=status.HTTP_400_BAD_REQUEST)

	return inner
