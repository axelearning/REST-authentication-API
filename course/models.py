from django.db import models
from authentication.models import User

# Create your models here.
class Course(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    author = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="Course")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)