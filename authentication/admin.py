from django.contrib import admin
from .models import User, Student, Teacher

# Register your models here.
@admin.register(User)
class User(admin.ModelAdmin):
    list_display = ['username']

@admin.register(Student)
class Student(admin.ModelAdmin):
    list_display = ['user']

@admin.register(Teacher)
class Teacher(admin.ModelAdmin):
    list_display = ['user']