from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter
from.models import JobApplication
from .serializers import JobApplicationSerializer

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
        
        
        