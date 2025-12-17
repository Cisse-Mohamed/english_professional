from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from apps.courses.models import Course, Assignment, Submission
from apps.chat.models import Message
from django.db.models import Q

@login_required
def dashboard(request):
    user = request.user
    today = timezone.now()

    # 1. Active Courses
    if user.is_instructor:
        courses = Course.objects.filter(instructor=user)
        active_courses_count = courses.count()
    else:
        courses = user.courses_enrolled.all()
        active_courses_count = courses.count()

    # 2. Pending Assignments (Context dependent)
    if user.is_instructor:
        # For instructors: Ungraded submissions
        # Submissions for assignments in their courses, where grade is null
        pending_assignments_count = Submission.objects.filter(
            assignment__lesson__course__instructor=user,
            grade__isnull=True
        ).count()
        pending_label = "Ungraded Submissions"
    else:
        # For students: Assignments due in future not yet submitted
        # Get assignments from enrolled courses that are due in the future
        # Exclude those that the user has already submitted
        pending_assignments_count = Assignment.objects.filter(
            lesson__course__in=courses,
            due_date__gte=today
        ).exclude(
            submissions__student=user
        ).count()
        pending_label = "Pending Assignments"

    # 3. Unread Messages
    unread_messages_count = Message.objects.filter(
        thread__participants=user,
        is_read=False
    ).exclude(sender=user).count()

    # 4. Learning Analytics (Quiz Performance)
    from apps.quiz.models import QuizSubmission
    recent_quizzes = QuizSubmission.objects.filter(student=user).order_by('submitted_at')[:5]
    
    quiz_labels = [q.quiz.title for q in recent_quizzes]
    # Calculate percentage score for each quiz
    quiz_scores = []
    for q in recent_quizzes:
        if q.total_questions > 0:
            percentage = (q.score / q.total_questions) * 100
            quiz_scores.append(round(percentage))
        else:
            quiz_scores.append(0)

    context = {
        'active_courses_count': active_courses_count,
        'pending_assignments_count': pending_assignments_count,
        'pending_label': pending_label,
        'unread_messages_count': unread_messages_count,
        'quiz_labels': quiz_labels,
        'quiz_scores': quiz_scores,
    }

    return render(request, 'dashboard/dashboard.html', context)

@login_required
def calendar_view(request):
    return render(request, 'dashboard/calendar.html')

@login_required
def calendar_events_api(request):
    user = request.user
    events = []
    
    # 1. Assignments (Due Dates)
    if user.is_instructor:
        courses = Course.objects.filter(instructor=user)
    else:
        courses = user.courses_enrolled.all()
        
    assignments = Assignment.objects.filter(lesson__course__in=courses)
    for assignment in assignments:
        events.append({
            'title': f"Deadline: {assignment.title}",
            'start': assignment.due_date.isoformat(),
            'url': f"/courses/assignments/{assignment.pk}/",
            'backgroundColor': '#ef4444', # Red
            'borderColor': '#ef4444'
        })
        
    # 2. Video Sessions
    # Note: Using string reference to avoid circular imports if needed, or import inside
    from apps.videoconference.models import VideoSession
    sessions = VideoSession.objects.filter(course__in=courses)
    for session in sessions:
        events.append({
            'title': f"Live: {session.title}",
            'start': session.start_time.isoformat(),
            'end': session.end_time.isoformat(),
            'url': session.meeting_url or '#',
            'backgroundColor': '#3b82f6', # Blue
            'borderColor': '#3b82f6'
        })
        
    from django.http import JsonResponse
    return JsonResponse(events, safe=False)
