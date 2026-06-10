from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobApplicationviewset

router = DefaultRouter()
router.register(r'jobs',JobApplicationviewset, basename='jobs')

urlpatterns = [
    path('',include(router.urls)),
]
