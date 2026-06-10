from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobApplicationviewset, generate_interview_questions

router = DefaultRouter()
router.register(r'jobs',JobApplicationviewset, basename='jobs')

urlpatterns = [
    path('',include(router.urls)),
    path('generate-questions/', generate_interview_questions, name='generate-questions'),
]
