from django.contrib import admin
from .models import StudentPerformanceSnapshot, CourseEngagementMetrics, StudentActivityLog


@admin.register(StudentPerformanceSnapshot)
class StudentPerformanceSnapshotAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'quiz_average', 'assignment_average', 'completion_rate', 'snapshot_date']
    list_filter = ['course', 'snapshot_date']
    search_fields = ['student__username', 'course__title']
    date_hierarchy = 'snapshot_date'


@admin.register(CourseEngagementMetrics)
class CourseEngagementMetricsAdmin(admin.ModelAdmin):
    list_display = ['course', 'total_students', 'active_students', 'average_completion_rate', 'calculated_at']
    list_filter = ['calculated_at']
    search_fields = ['course__title']
    date_hierarchy = 'calculated_at'


@admin.register(StudentActivityLog)
class StudentActivityLogAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'activity_type', 'timestamp']
    list_filter = ['activity_type', 'timestamp', 'course']
    search_fields = ['student__username', 'course__title']
    date_hierarchy = 'timestamp'