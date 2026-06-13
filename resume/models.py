from django.db import models
from django.contrib.auth.models import User


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')

    # Personal Info
    full_name    = models.CharField(max_length=255)
    email        = models.EmailField()
    phone        = models.CharField(max_length=20, blank=True)
    location     = models.CharField(max_length=255, blank=True)
    linkedin = models.CharField(max_length=255, blank=True)
    github   = models.CharField(max_length=255, blank=True)

    # AI Generated
    summary      = models.TextField(blank=True)

    # Meta
    title        = models.CharField(max_length=255)  # e.g. "Python Developer Resume"
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    
    # ATS
    job_description  = models.TextField(blank=True)  # paste JD here
    ats_score        = models.IntegerField(default=0) # AI estimated match %
    target_role      = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    class Meta:
        ordering = ['-created_at']


class Education(models.Model):
    resume      = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='education')
    degree      = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    year        = models.CharField(max_length=10)
    grade       = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class Experience(models.Model):
    resume      = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experience')
    company     = models.CharField(max_length=255)
    role        = models.CharField(max_length=255)
    start_date  = models.CharField(max_length=20)
    end_date    = models.CharField(max_length=20, blank=True, default='Present')
    description = models.TextField(blank=True)

    # AI generated bullet points
    ai_bullets  = models.TextField(blank=True)

    def __str__(self):
        return f"{self.role} at {self.company}"


class Skill(models.Model):
    resume   = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills')
    category = models.CharField(max_length=100)  # e.g. "Languages", "Frameworks"
    items    = models.CharField(max_length=500)  # e.g. "Python, Django, DRF"

    def __str__(self):
        return f"{self.category}: {self.items}"
    
    