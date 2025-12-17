from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course_list'),
    path('create/', views.CourseCreateView.as_view(), name='course_create'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    
    # Lessons
    path('<int:course_id>/lessons/create/', views.LessonCreateView.as_view(), name='lesson_create'),
    path('<int:course_id>/lessons/<int:lesson_id>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    
    # Assignments
    path('<int:course_id>/lessons/<int:lesson_id>/assignment/create/', views.AssignmentCreateView.as_view(), name='assignment_create'),
    path('assignment/<int:assignment_id>/', views.AssignmentDetailView.as_view(), name='assignment_detail'),
    path('assignments/user/<int:user_id>/', views.UserAssignmentsView.as_view(), name='user_assignments'),
    
    # Progress
    path('lesson/<int:lesson_id>/complete/', views.toggle_lesson_completion, name='toggle_lesson_completion'),
]
