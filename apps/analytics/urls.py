from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Student performance
    path('student/<int:course_id>/', views.student_performance_dashboard, name='student_performance'),
    
    # Instructor analytics
    path('instructor/<int:course_id>/', views.instructor_analytics_dashboard, name='instructor_analytics'),
    
    # Exports
    path('export/students/<int:course_id>/csv/', views.export_student_performance_csv, name='export_students_csv'),
    path('export/engagement/<int:course_id>/csv/', views.export_engagement_report_csv, name='export_engagement_csv'),
    
    # API endpoints
    path('api/trends/<int:course_id>/', views.api_performance_trends, name='api_trends'),
    path('api/engagement/<int:course_id>/', views.api_course_engagement, name='api_engagement'),
]