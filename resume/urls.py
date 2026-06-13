from django.urls import path
from .views import ResumeListCreateView, ResumeDetailView, generate_resume_ai, generate_pdf

urlpatterns = [
    path('resumes/', ResumeListCreateView.as_view(), name='resume-list'),
    path('resumes/<int:pk>/', ResumeDetailView.as_view(), name='resume-detail'),
    path('resumes/<int:pk>/generate/', generate_resume_ai, name='resume-generate'),
    path('resumes/<int:pk>/pdf/', generate_pdf, name='resume-pdf'),
]