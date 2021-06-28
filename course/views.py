
from rest_framework import generics, permissions

from .serializers import CourseSerializer
from .models import Course
from .permissions import IsOwnerOrReadOnly


# Create your views here.

class CoursesListAPIView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user) 

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if not user.is_anonymous:
            if user.is_teacher:
                queryset = self.queryset.filter(author=user)
        return queryset


class DeleteUpdateCourseAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (IsOwnerOrReadOnly,)

