from rest_framework import serializers
from .models import JobApplication

class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        exclude = ['user']
        read_only_fields = ['id','created_at','updated_at']