from rest_framework import serializers
from .models import Resume, Education, Experience, Skill


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        exclude = ['resume']


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        exclude = ['resume']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        exclude = ['resume']


class ResumeSerializer(serializers.ModelSerializer):
    education  = EducationSerializer(many=True, read_only=True)
    experience = ExperienceSerializer(many=True, read_only=True)
    skills     = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = Resume
        exclude = ['user']
        read_only_fields = ['id', 'summary', 'ats_score', 'created_at', 'updated_at']


class ResumeCreateSerializer(serializers.ModelSerializer):
    education  = EducationSerializer(many=True)
    experience = ExperienceSerializer(many=True)
    skills     = SkillSerializer(many=True)

    class Meta:
        model = Resume
        exclude = ['user', 'summary', 'ats_score']

    def create(self, validated_data):
        education_data  = validated_data.pop('education', [])
        experience_data = validated_data.pop('experience', [])
        skills_data     = validated_data.pop('skills', [])

        resume = Resume.objects.create(**validated_data)

        for edu in education_data:
            Education.objects.create(resume=resume, **edu)

        for exp in experience_data:
            Experience.objects.create(resume=resume, **exp)

        for skill in skills_data:
            Skill.objects.create(resume=resume, **skill)

        return resume