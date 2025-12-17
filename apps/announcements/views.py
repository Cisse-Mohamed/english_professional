from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q

from .models import Announcement, AnnouncementRead
from apps.courses.models import Course


@login_required
def announcement_list(request):
    """List all announcements visible to the user"""
    user = request.user
    
    # Get platform-wide announcements
    platform_announcements = Announcement.objects.filter(scope='platform')
    
    # Get course-specific announcements from enrolled courses
    if user.is_instructor:
        courses = Course.objects.filter(instructor=user)
    else:
        courses = user.courses_enrolled.all()
    
    course_announcements = Announcement.objects.filter(
        scope='course',
        course__in=courses
    )
    
    # Combine and order
    all_announcements = (platform_announcements | course_announcements).distinct().order_by('-is_pinned', '-created_at')
    
    # Mark unread announcements
    read_ids = AnnouncementRead.objects.filter(user=user).values_list('announcement_id', flat=True)
    
    announcements_data = []
    for announcement in all_announcements:
        announcements_data.append({
            'announcement': announcement,
            'is_read': announcement.id in read_ids
        })
    
    context = {
        'announcements_data': announcements_data,
    }
    
    return render(request, 'announcements/announcement_list.html', context)


@login_required
def announcement_detail(request, announcement_id):
    """View announcement detail and mark as read"""
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    # Check if user should have access
    if announcement.scope == 'platform':
        has_access = True
    elif announcement.scope == 'course':
        has_access = (
            announcement.course.students.filter(id=request.user.id).exists() or
            announcement.course.instructor == request.user
        )
    else:
        has_access = False
    
    if not has_access:
        return HttpResponse("Unauthorized", status=403)
    
    # Mark as read
    AnnouncementRead.objects.get_or_create(
        announcement=announcement,
        user=request.user
    )
    
    context = {
        'announcement': announcement,
    }
    
    return render(request, 'announcements/announcement_detail.html', context)


@login_required
def announcement_create(request):
    """Create a new announcement (instructors and staff only)"""
    if not (request.user.is_instructor or request.user.is_staff):
        return HttpResponse("Unauthorized", status=403)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        scope = request.POST.get('scope')
        course_id = request.POST.get('course_id')
        priority = request.POST.get('priority', 'medium')
        send_email = request.POST.get('send_email') == 'on'
        is_pinned = request.POST.get('is_pinned') == 'on'
        
        # Validate
        if scope == 'course' and not course_id:
            messages.error(request, "Course is required for course-specific announcements")
            return redirect('announcements:create')
        
        # Create announcement
        announcement = Announcement.objects.create(
            title=title,
            content=content,
            author=request.user,
            scope=scope,
            course_id=course_id if scope == 'course' else None,
            priority=priority,
            send_email=send_email,
            is_pinned=is_pinned
        )
        
        messages.success(request, "Announcement created successfully!")
        return redirect('announcements:detail', announcement_id=announcement.id)
    
    # Get courses for dropdown
    if request.user.is_staff:
        courses = Course.objects.all()
    else:
        courses = Course.objects.filter(instructor=request.user)
    
    context = {
        'courses': courses,
    }
    
    return render(request, 'announcements/announcement_create.html', context)


@login_required
@require_POST
def mark_announcement_read(request, announcement_id):
    """Mark announcement as read via AJAX"""
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    AnnouncementRead.objects.get_or_create(
        announcement=announcement,
        user=request.user
    )
    
    return JsonResponse({'status': 'success'})


@login_required
def unread_announcements_count(request):
    """Get count of unread announcements"""
    user = request.user
    
    # Get all visible announcements
    if user.is_instructor:
        courses = Course.objects.filter(instructor=user)
    else:
        courses = user.courses_enrolled.all()
    
    all_announcements = Announcement.objects.filter(
        Q(scope='platform') | Q(scope='course', course__in=courses)
    ).distinct()
    
    # Get read announcements
    read_ids = AnnouncementRead.objects.filter(user=user).values_list('announcement_id', flat=True)
    
    unread_count = all_announcements.exclude(id__in=read_ids).count()
    
    return JsonResponse({'unread_count': unread_count})