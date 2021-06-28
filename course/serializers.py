from rest_framework import serializers
from .models import Course



class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['title', 'content', 'created_at', 'updated_at', 'author']
        extra_kwargs = {
            'author': {'read_only': True},
        }