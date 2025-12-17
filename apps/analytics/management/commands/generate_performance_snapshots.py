from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.courses.models import Course
from apps.analytics.utils import create_performance_snapshot, calculate_course_engagement


class Command(BaseCommand):
    help = 'Generate performance snapshots for all students in all courses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--course-id',
            type=int,
            help='Generate snapshots for a specific course only',
        )

    def handle(self, *args, **options):
        course_id = options.get('course_id')
        
        if course_id:
            courses = Course.objects.filter(id=course_id)
        else:
            courses = Course.objects.all()
        
        total_snapshots = 0
        total_metrics = 0
        
        for course in courses:
            self.stdout.write(f"Processing course: {course.title}")
            
            # Generate student snapshots
            for student in course.students.all():
                create_performance_snapshot(student, course)
                total_snapshots += 1
            
            # Calculate course engagement metrics
            calculate_course_engagement(course)
            total_metrics += 1
            
            self.stdout.write(
                self.style.SUCCESS(f"  Created {course.students.count()} snapshots")
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted! Generated {total_snapshots} student snapshots and {total_metrics} course metrics"
            )
        )