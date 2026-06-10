from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter
from.models import JobApplication
from .serializers import JobApplicationSerializer
import google.generativeai as genai
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_interview_questions(request):
    company = request.data.get('company', '')
    role    = request.data.get('role', '')

    if not company or not role:
        return Response(
            {'error': 'Company and role are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = f"""
You are an expert technical interviewer.
Generate 10 interview questions for a {role} position at {company}.

Include a mix of:
- 3 technical questions specific to the role
- 3 behavioral questions
- 2 company-specific questions
- 2 situational questions

Format each question on a new line starting with a number like:
1. Question here
2. Question here

Keep questions concise and realistic.
"""
        response = model.generate_content(prompt)
        questions_text = response.text

        lines = questions_text.strip().split('\n')
        questions = [
            line.strip() for line in lines
            if line.strip() and line.strip()[0].isdigit()
        ]

        return Response({'questions': questions})

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class JobApplicationviewset(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['company', 'role', 'status']
    
    def get_queryset(self):
        queryset = JobApplication.objects.filter(user=self.request.user)
        status = self.request.query_params.get('status',None)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset
    
    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)
        
        
        