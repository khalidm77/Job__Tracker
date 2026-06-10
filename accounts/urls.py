from django.urls import path
from .views import RegisterView, ProfileView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('register/', RegisterView.as_view(), name = 'Register_user'),
    path('login/',TokenObtainPairView.as_view(), name = 'Login'),
    path('Refresh/',TokenRefreshView.as_view(), name = 'Refresh'),
    path('Profile/',ProfileView.as_view(), name = 'Profile')
]
