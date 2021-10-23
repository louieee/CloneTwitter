# accounts/urls.py

from django.contrib.auth.decorators import login_required
from django.urls import path
# RESTFRAMEWORK imports
from rest_framework.routers import DefaultRouter

# View and other imports
from .views import *

app_name = 'Account'

router = DefaultRouter()
router.register('user/signup', Signup, basename="user")




urlpatterns = [
	path('user/', UserProfile.as_view(), name="user_profile"),
    path('user/login/', Login.as_view(),name="login"),
	path('user/edit/', EditUser.as_view(), name="edit_user"),
	path('user/<int:id>/action/', ActionUser.as_view(), name="user_action")


]
urlpatterns += router.urls

