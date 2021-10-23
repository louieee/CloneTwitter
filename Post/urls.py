# accounts/urls.py

from django.contrib.auth.decorators import login_required
from django.urls import path
# RESTFRAMEWORK imports
from rest_framework.routers import DefaultRouter

# View and other imports
from .views import *

app_name = 'Post'

router = DefaultRouter()
router.register(r'post', ReadListDeletePost , basename="post")

urlpatterns = [
	path('post/create/', CreatePost.as_view({"post" : "create"}), name="create_post"),
	path('post/<int:pk>/edit/', EditPost.as_view({"patch": "partial_update"}), name="edit_post"),
	path('post/feeds/refresh/', RefreshPosts.as_view(), name="refresh_posts")

]
urlpatterns += router.urls

