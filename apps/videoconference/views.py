import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt 
from django.db import transaction, IntegrityError
from django.urls import reverse
from django.utils import timezone 

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .decorators import instructor_required_for_session, instructor_required_for_recording 
from .models import VideoSession, BreakoutRoom, VideoSessionParticipant, VideoRecording, InstantVideoSession, InstantVideoSessionParticipant 

from apps.courses.models import Course 
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


@login_required
def index(request):
    return render(request, 'videoconference/index.html')

@login_required
def room(request, session_slug, breakout_slug=None):
    video_session = get_object_or_404(VideoSession, meeting_url=session_slug)
    
    # Check if user is an instructor/host for the course related to this video session
    is_host = video_session.course.instructors.filter(id=request.user.id).exists()

    # If a breakout_slug is provided, ensure the breakout room exists
    if breakout_slug:
        get_object_or_404(BreakoutRoom, session=video_session, slug=breakout_slug)

    context = {
        'session_slug': session_slug,
        'breakout_slug': breakout_slug,
        'is_host': is_host,
        'video_session_id': video_session.id, # Pass the ID for API calls
    }
    return render(request, 'videoconference/room.html', context)


@login_required
@require_POST
def create_instant_session(request):
    title = request.POST.get('title')
    if not title:
        title = f"Instant Session by {request.user.username}"

    try:
        instant_session = InstantVideoSession.objects.create(
            title=title,
            creator=request.user
        )
        return redirect(reverse('videoconference:join_instant_session', args=[instant_session.slug]))
    except Exception as e:
        logger.exception("Error creating instant session.")
        return JsonResponse({'error': f'Failed to create instant session: {str(e)}'}, status=500)

@login_required
def join_instant_session(request, slug):
    instant_session = get_object_or_404(InstantVideoSession, slug=slug)

    context = {
        'session_slug': instant_session.slug,
        'session_title': instant_session.title,
        'is_host': (request.user == instant_session.creator),
        'session_type': 'instant', # Indicate this is an instant session
    }
    return render(request, 'videoconference/instant_room.html', context)


@login_required
@require_POST
@csrf_exempt
@instructor_required_for_session
def create_breakout_room(request):
    session_id = request.POST.get('session_id')
    room_name = request.POST.get('room_name')

    if not room_name:
        return JsonResponse({'error': 'Room name is required.'}, status=400)

    try:
        session = get_object_or_404(VideoSession, id=session_id)
        
        with transaction.atomic():
            breakout_room = BreakoutRoom.objects.create(session=session, name=room_name)
            
            # Signal to group
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'video_main_{session.meeting_url}',
                {
                    'type': 'video_signal',
                    'action': 'breakout_room_created',
                    'data': {
                        'id': breakout_room.id,
                        'name': breakout_room.name,
                        'slug': breakout_room.slug
                    },
                    'sender': 'system'
                }
            )

            return JsonResponse({
                'id': breakout_room.id,
                'name': breakout_room.name,
                'slug': breakout_room.slug,
                'is_active': breakout_room.is_active,
                'session_id': session.id
            }, status=201)
    except IntegrityError as e:
        logger.error(f"Integrity error creating breakout room: {e}")
        return JsonResponse({'error': 'Failed to create breakout room due to data integrity issue, possibly a duplicate name.'}, status=400)
    except Exception as e:
        logger.exception("An unexpected error occurred while creating a breakout room.")
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)

@login_required
@require_GET
def list_breakout_rooms(request):
    session_id = request.GET.get('session_id')

    if not session_id:
        return JsonResponse({'error': 'Session ID is required.'}, status=400)
    
    try:
        session = get_object_or_404(VideoSession, id=session_id)
        # Participants or instructors can list breakout rooms
        is_participant = VideoSessionParticipant.objects.filter(user=request.user, session=session).exists()
        is_instructor = session.course.instructors.filter(id=request.user.id).exists()
        
        if not (is_participant or is_instructor):
            return JsonResponse({'error': 'You do not have permission to view breakout rooms for this session.'}, status=403)

        breakout_rooms = BreakoutRoom.objects.filter(session=session, is_active=True).values('id', 'name', 'slug')
        return JsonResponse({'breakout_rooms': list(breakout_rooms)}, status=200)
    except VideoSession.DoesNotExist:
        logger.warning(f"Video session with ID {session_id} not found for list_breakout_rooms.")
        return JsonResponse({'error': 'Video session not found.'}, status=404)
    except Exception as e:
        logger.exception("An unexpected error occurred while listing breakout rooms.")
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)

@login_required
@require_POST
@csrf_exempt 
@instructor_required_for_session
def assign_participant_to_breakout_room(request):
    session_id = request.POST.get('session_id')
    participant_user_id = request.POST.get('user_id')
    breakout_room_id = request.POST.get('breakout_room_id') 

    if not participant_user_id:
        return JsonResponse({'error': 'Participant User ID is required.'}, status=400)
    
    try:
        session = get_object_or_404(VideoSession, id=session_id)
        
        participant_user = get_object_or_404(User, id=participant_user_id)
        
        with transaction.atomic():
            participant, created = VideoSessionParticipant.objects.get_or_create(
                user=participant_user,
                session=session,
                defaults={'is_host': False} 
            )

            breakout_room = None
            breakout_slug = None
            if breakout_room_id:
                breakout_room = get_object_or_404(BreakoutRoom, id=breakout_room_id, session=session)
                breakout_slug = breakout_room.slug
            
            participant.breakout_room = breakout_room
            participant.save() 

            # Signal to user
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'video_main_{session.meeting_url}',
                {
                    'type': 'video_signal',
                    'action': 'user_assigned_to_breakout',
                    'data': {
                        'username': participant_user.username,
                        'breakout_slug': breakout_slug
                    },
                    'target': participant_user.username,
                    'sender': 'system'
                }
            )

            return JsonResponse({
                'message': 'Participant assigned successfully.',
                'participant_id': participant.id,
                'user_id': participant.user.id,
                'breakout_room_id': breakout_room.id if breakout_room else None,
                'session_id': session.id
            }, status=200)
    except User.DoesNotExist:
        logger.warning(f"Participant user with ID {participant_user_id} not found for session {session_id}.")
        return JsonResponse({'error': 'Participant user not found.'}, status=404)
    except BreakoutRoom.DoesNotExist:
        logger.warning(f"Breakout room with ID {breakout_room_id} not found for session {session_id}.")
        return JsonResponse({'error': 'Breakout room not found.'}, status=404)
    except IntegrityError as e:
        logger.error(f"Integrity error assigning participant to breakout room: {e}")
        return JsonResponse({'error': 'Failed to assign participant due to data integrity issue.'}, status=400)
    except Exception as e:
        logger.exception("An unexpected error occurred while assigning participant to a breakout room.")
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)


@login_required
@require_POST
@csrf_exempt
@instructor_required_for_session
def start_recording(request):
    session_id = request.POST.get('session_id') 
    
    try:
        session = get_object_or_404(VideoSession, id=session_id)
        
        with transaction.atomic():
            # Check if there's an ongoing recording for this session
            active_recording = VideoRecording.objects.filter(session=session, end_time__isnull=True).first()
            if active_recording:
                return JsonResponse({'error': 'A recording is already in progress for this session.'}, status=409) 
            
            recording = VideoRecording.objects.create(
                session=session,
                recorded_by=request.user,
                start_time=timezone.now(),
                title=f"Recording for {session.title} - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            )

            # Signal to group
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'video_main_{session.meeting_url}',
                {
                    'type': 'video_signal',
                    'action': 'recording_started',
                    'data': {
                        'recording_id': recording.id,
                        'started_by': request.user.username
                    },
                    'sender': 'system'
                }
            )

            return JsonResponse({
                'message': 'Recording started.',
                'recording_id': recording.id,
                'start_time': recording.start_time
            }, status=200)
    except IntegrityError as e:
        logger.error(f"Integrity error starting recording for session {session_id}: {e}")
        return JsonResponse({'error': 'Failed to start recording due to a database issue.'}, status=400)
    except Exception as e:
        logger.exception("An unexpected error occurred while starting a recording.")
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)


@login_required
@require_POST
@csrf_exempt
@instructor_required_for_recording
def stop_recording(request):
    recording_id = request.POST.get('recording_id') 
    
    try:
        recording = get_object_or_404(VideoRecording, id=recording_id) 
        
        if recording.end_time is not None:
            return JsonResponse({'error': 'Recording has already been stopped.'}, status=409)
        
        with transaction.atomic():
            recording.end_time = timezone.now()
            # Placeholder for actual file_url from external recording service
            recording.file_url = f"/media/recordings/{recording.session.id}_{recording.id}.webm"
            recording.save()

            # Signal to group
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'video_main_{recording.session.meeting_url}',
                {
                    'type': 'video_signal',
                    'action': 'recording_stopped',
                    'data': {
                        'recording_id': recording.id,
                        'file_url': recording.file_url,
                        'stopped_by': request.user.username
                    },
                    'sender': 'system'
                }
            )

            return JsonResponse({'message': 'Recording stopped.', 'recording_id': recording.id, 'file_url': recording.file_url}, status=200)
    except IntegrityError as e:
        logger.error(f"Integrity error stopping recording {recording_id}: {e}")
        return JsonResponse({'error': 'Failed to stop recording due to a database issue.'}, status=400)
    except Exception as e:
        logger.exception("An unexpected error occurred while stopping a recording.")
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)


@login_required
@require_GET
def list_recordings(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return JsonResponse({'error': 'Session ID is required.'}, status=400)
    
    try:
        session = get_object_or_404(VideoSession, id=session_id)
        # Check if user is a participant or instructor to view recordings
        is_participant = VideoSessionParticipant.objects.filter(user=request.user, session=session).exists()
        is_instructor = session.course.instructors.filter(id=request.user.id).exists()

        if not (is_participant or is_instructor):
            return JsonResponse({'error': 'You do not have permission to view recordings for this session.'}, status=403)
        
        recordings = VideoRecording.objects.filter(session=session).order_by('-start_time')
        recordings_data = [{
            'id': rec.id,
            'title': rec.title if rec.title else f"Recording from {rec.start_time.strftime('%Y-%m-%d %H:%M')}",
            'start_time': rec.start_time.isoformat(),
            'end_time': rec.end_time.isoformat() if rec.end_time else None,
            'file_url': rec.file_url
        } for rec in recordings]
        
        return JsonResponse({'recordings': recordings_data}, status=200)
    except VideoSession.DoesNotExist:
        logger.warning(f"Video session with ID {session_id} not found for list_recordings.")
        return JsonResponse({'error': 'Video session not found.'}, status=404)
    except Exception as e:
        logger.exception("An unexpected error occurred while listing recordings.")
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)


@login_required
@require_GET
@instructor_required_for_session
def list_attendance(request):
    session_id = request.GET.get('session_id')
    
    try:
        session = get_object_or_404(VideoSession, id=session_id) 
        
        participants = VideoSessionParticipant.objects.filter(session=session).select_related('user', 'breakout_room').order_by('joined_at')
        attendance_data = [{
            'username': p.user.username,
            'joined_at': p.joined_at.isoformat(),
            'left_at': p.left_at.isoformat() if p.left_at else None,
            'is_host': p.is_host,
            'breakout_room': p.breakout_room.name if p.breakout_room else 'Main Room'
        } for p in participants]
        
        return JsonResponse({'attendance': attendance_data}, status=200)
    except Exception as e:
        logger.exception("An unexpected error occurred while listing attendance.")
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)

