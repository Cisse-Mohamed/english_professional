from django.db.models import Avg, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from apps.courses.models import Course, LessonProgress, Submission
from apps.quiz.models import QuizSubmission
from apps.forum.models import DiscussionThread, DiscussionPost
from .models import StudentPerformanceSnapshot, CourseEngagementMetrics, StudentActivityLog


def calculate_student_performance(student, course):
    """Calculate comprehensive performance metrics for a student in a course"""
    
    # Quiz average
    quiz_submissions = QuizSubmission.objects.filter(
        student=student,
        quiz__lesson__course=course
    )
    if quiz_submissions.exists():
        quiz_avg = sum(
            (q.score / q.total_questions * 100) if q.total_questions > 0 else 0
            for q in quiz_submissions
        ) / quiz_submissions.count()
    else:
        quiz_avg = 0.0
    
    # Assignment average
    submissions = Submission.objects.filter(
        student=student,
        assignment__lesson__course=course,
        grade__isnull=False
    )
    assignment_avg = submissions.aggregate(avg=Avg('grade'))['avg'] or 0.0
    
    # Completion rate
    total_lessons = course.lessons.count()
    completed_lessons = LessonProgress.objects.filter(
        student=student,
        lesson__course=course,
        is_completed=True
    ).count()
    completion_rate = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0.0
    
    # Engagement score (composite metric)
    # Based on: quiz performance (30%), assignment grades (30%), completion rate (20%), forum activity (20%)
    forum_posts = DiscussionPost.objects.filter(
        author=student,
        thread__course=course
    ).count()
    forum_threads = DiscussionThread.objects.filter(
        author=student,
        course=course
    ).count()
    forum_activity = min((forum_posts + forum_threads * 2) / 10 * 100, 100)  # Cap at 100
    
    engagement_score = (
        quiz_avg * 0.3 +
        assignment_avg * 0.3 +
        completion_rate * 0.2 +
        forum_activity * 0.2
    )
    
    return {
        'quiz_average': round(quiz_avg, 2),
        'assignment_average': round(assignment_avg, 2),
        'completion_rate': round(completion_rate, 2),
        'engagement_score': round(engagement_score, 2),
    }


def create_performance_snapshot(student, course):
    """Create a performance snapshot for a student"""
    metrics = calculate_student_performance(student, course)
    
    snapshot = StudentPerformanceSnapshot.objects.create(
        student=student,
        course=course,
        **metrics
    )
    return snapshot


def calculate_course_engagement(course):
    """Calculate engagement metrics for a course"""
    total_students = course.students.count()
    
    # Active students (activity in last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    active_students = StudentActivityLog.objects.filter(
        course=course,
        timestamp__gte=seven_days_ago
    ).values('student').distinct().count()
    
    # Average completion rate
    if total_students > 0:
        total_lessons = course.lessons.count()
        if total_lessons > 0:
            completion_rates = []
            for student in course.students.all():
                completed = LessonProgress.objects.filter(
                    student=student,
                    lesson__course=course,
                    is_completed=True
                ).count()
                completion_rates.append((completed / total_lessons) * 100)
            avg_completion = sum(completion_rates) / len(completion_rates) if completion_rates else 0
        else:
            avg_completion = 0
    else:
        avg_completion = 0
    
    # Average quiz score
    quiz_submissions = QuizSubmission.objects.filter(
        quiz__lesson__course=course
    )
    if quiz_submissions.exists():
        avg_quiz = sum(
            (q.score / q.total_questions * 100) if q.total_questions > 0 else 0
            for q in quiz_submissions
        ) / quiz_submissions.count()
    else:
        avg_quiz = 0
    
    # Forum activity
    forum_activity = (
        DiscussionThread.objects.filter(course=course).count() +
        DiscussionPost.objects.filter(thread__course=course).count()
    )
    
    # Dropout risk (students with < 20% completion and no activity in 14 days)
    fourteen_days_ago = timezone.now() - timedelta(days=14)
    at_risk_students = 0
    for student in course.students.all():
        metrics = calculate_student_performance(student, course)
        recent_activity = StudentActivityLog.objects.filter(
            student=student,
            course=course,
            timestamp__gte=fourteen_days_ago
        ).exists()
        
        if metrics['completion_rate'] < 20 and not recent_activity:
            at_risk_students += 1
    
    metrics = CourseEngagementMetrics.objects.create(
        course=course,
        total_students=total_students,
        active_students=active_students,
        average_completion_rate=round(avg_completion, 2),
        average_quiz_score=round(avg_quiz, 2),
        forum_activity_count=forum_activity,
        dropout_risk_count=at_risk_students
    )
    
    return metrics


def log_student_activity(student, activity_type, course=None, **kwargs):
    """Log a student activity"""
    return StudentActivityLog.objects.create(
        student=student,
        course=course,
        activity_type=activity_type,
        activity_data=kwargs
    )


def get_performance_trends(student, course, days=30):
    """Get performance trends over time"""
    start_date = timezone.now() - timedelta(days=days)
    snapshots = StudentPerformanceSnapshot.objects.filter(
        student=student,
        course=course,
        snapshot_date__gte=start_date
    ).order_by('snapshot_date')
    
    return {
        'dates': [s.snapshot_date.strftime('%Y-%m-%d') for s in snapshots],
        'quiz_scores': [s.quiz_average for s in snapshots],
        'assignment_scores': [s.assignment_average for s in snapshots],
        'completion_rates': [s.completion_rate for s in snapshots],
        'engagement_scores': [s.engagement_score for s in snapshots],
    }


def get_student_heatmap_data(course):
    """Generate heatmap data for student progress in course"""
    students = course.students.all()
    lessons = course.lessons.all().order_by('order')
    
    heatmap_data = []
    for student in students:
        student_row = {
            'student_id': student.id,
            'student_name': student.get_full_name() or student.username,
            'lessons': []
        }
        
        for lesson in lessons:
            progress = LessonProgress.objects.filter(
                student=student,
                lesson=lesson
            ).first()
            
            # Get quiz score for this lesson if exists
            quiz_score = None
            if hasattr(lesson, 'quiz'):
                submission = QuizSubmission.objects.filter(
                    student=student,
                    quiz=lesson.quiz
                ).first()
                if submission and submission.total_questions > 0:
                    quiz_score = (submission.score / submission.total_questions) * 100
            
            student_row['lessons'].append({
                'lesson_id': lesson.id,
                'lesson_title': lesson.title,
                'completed': progress.is_completed if progress else False,
                'quiz_score': round(quiz_score, 1) if quiz_score is not None else None,
            })
        
        heatmap_data.append(student_row)
    
    return heatmap_data