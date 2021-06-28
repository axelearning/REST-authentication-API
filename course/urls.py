from course.serializers import CourseSerializer
from django.urls import path
from . import views

urlpatterns = [
    path('', views.CoursesListAPIView.as_view() ,name='courses'),
    path('<int:pk>', views.DeleteUpdateCourseAPIView.as_view() ,name='course'),
]