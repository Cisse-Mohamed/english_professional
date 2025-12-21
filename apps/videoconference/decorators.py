from functools import wraps
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import VideoSession, VideoRecording

def instructor_required_for_session(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        session_id = request.POST.get('session_id') or request.GET.get('session_id')
        
        if not session_id:
            return JsonResponse({'error': 'Session ID is required.'}, status=400)
            
        session = get_object_or_404(VideoSession, id=session_id)
        
        if not session.course.instructors.filter(id=request.user.id).exists():
            return JsonResponse({'error': 'You do not have permission to perform this action.'}, status=403)
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def instructor_required_for_recording(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        recording_id = request.POST.get('recording_id') or request.GET.get('recording_id')

        if not recording_id:
            return JsonResponse({'error': 'Recording ID is required.'}, status=400)

        recording = get_object_or_404(VideoRecording, id=recording_id)

        if not recording.session.course.instructors.filter(id=request.user.id).exists():
            return JsonResponse({'error': 'You do not have permission to perform this action on this recording.'}, status=403)
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view
