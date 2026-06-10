from django.db import models
from django.contrib.auth.models import User

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('applied','Applied'),
        ('interview','Interview'),
        ('offer','Offer'),
        ('rejected','Rejected'),
    ]
    
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='applications')
    company = models.CharField(max_length=50)
    role = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    date_applied = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.comapany} - {self.role} ({self.status})"
    
    class Meta:
        ordering = ['-date_applied']