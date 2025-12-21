import logging
import json

logger = logging.getLogger(__name__)
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import VideoSession, BreakoutRoom, VideoSessionParticipant, VideoRecording, InstantVideoSession, InstantVideoSessionParticipant
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone # Import timezone

User = get_user_model()

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_type = self.scope['url_route']['kwargs'].get('session_type') # 'regular' or 'instant'
        self.session_slug = self.scope['url_route']['kwargs'].get('session_slug')
        self.breakout_slug = self.scope['url_route']['kwargs'].get('breakout_slug')

        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        self.is_instant_session = (self.session_type == 'instant')
        self.current_session_object = None # Either VideoSession or InstantVideoSession
        self.participant_object = None # Either VideoSessionParticipant or InstantVideoSessionParticipant

        if self.is_instant_session:
            try:
                self.current_session_object = await sync_to_async(InstantVideoSession.objects.get)(slug=self.session_slug)
            except InstantVideoSession.DoesNotExist:
                logger.warning(f"InstantVideoSession with slug {self.session_slug} not found during WebSocket connection.")
                await self.close()
                return
            except Exception:
                logger.exception(f"An unexpected error occurred while fetching InstantVideoSession {self.session_slug} during connect.")
                await self.close()
                return
            
            self.room_group_name = f"instant_video_{self.session_slug}"

            self.participant_object, created = await sync_to_async(InstantVideoSessionParticipant.objects.get_or_create)(
                user=self.scope["user"],
                session=self.current_session_object,
                defaults={'is_host': False}
            )
            if not created:
                self.participant_object.left_at = None # Reset left_at if rejoining
            
            # Creator is host for instant sessions
            if self.scope["user"] == self.current_session_object.creator:
                self.participant_object.is_host = True

        else: # Regular VideoSession
            try:
                self.current_session_object = await sync_to_async(VideoSession.objects.get)(meeting_url=self.session_slug)
            except VideoSession.DoesNotExist:
                logger.warning(f"VideoSession with slug {self.session_slug} not found during WebSocket connection.")
                await self.close()
                return
            except Exception:
                logger.exception(f"An unexpected error occurred while fetching VideoSession {self.session_slug} during connect.")
                await self.close()
                return

            self.breakout_room = None
            if self.breakout_slug:
                try:
                    self.breakout_room = await sync_to_async(BreakoutRoom.objects.get)(session=self.current_session_object, slug=self.breakout_slug)
                except BreakoutRoom.DoesNotExist:
                    logger.warning(f"BreakoutRoom with slug {self.breakout_slug} not found for session {self.session_slug} during WebSocket connection.")
                    await self.close()
                    return
                except Exception:
                    logger.exception(f"An unexpected error occurred while fetching BreakoutRoom {self.breakout_slug} during connect.")
                    await self.close()
                    return
                self.room_group_name = 'video_breakout_%s_%s' % (self.session_slug, self.breakout_slug)
            else:
                self.room_group_name = 'video_main_%s' % self.session_slug
            
            self.participant_object, created = await sync_to_async(VideoSessionParticipant.objects.get_or_create)(
                user=self.scope["user"],
                session=self.current_session_object,
                defaults={'breakout_room': self.breakout_room, 'is_host': False}
            )
            if not created: 
                self.participant_object.breakout_room = self.breakout_room
                self.participant_object.left_at = None
            
            is_host_user = await sync_to_async(lambda: self.scope["user"] in self.current_session_object.course.instructors.all())()
            if is_host_user:
                self.participant_object.is_host = True
        
        await sync_to_async(self.participant_object.save)()

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # Update participant's left_at timestamp
        if self.scope["user"].is_authenticated and hasattr(self, 'participant_object') and self.participant_object:
            self.participant_object.left_at = timezone.now()
            await sync_to_async(self.participant_object.save)()
        
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')
        target = text_data_json.get('target') # Username of specific recipient
        data = text_data_json.get('data')
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'video_signal',
                'action': action,
                'data': data,
                'target': target,
                'sender': self.scope['user'].username
            }
        )

    # Receive message from room group
    async def video_signal(self, event):
        action = event['action']
        data = event['data']
        sender = event['sender']
        target = event.get('target')

        # Send message to WebSocket
        # Logic: 
        # 1. If 'target' is specified, only send if self.user.username == target
        # 2. If 'target' is NOT specified, broadcast to everyone except sender
        
        should_send = False
        if target:
            if target == self.scope['user'].username:
                should_send = True
        else:
            if sender != self.scope['user'].username:
                should_send = True
        
        # Add screen sharing specific actions to be broadcasted
        screen_share_actions = [
            'screen_share_start', 'screen_share_stop', 'screen_share_offer', 
            'screen_share_answer', 'screen_share_candidate'
        ]
        
        # Recording specific actions
        recording_actions = ['recording_started', 'recording_stopped']

        # Breakout room specific actions (for clients to update UI/reconnect)
        breakout_actions = ['breakout_room_created', 'user_assigned_to_breakout', 'breakout_room_closed']

        if should_send or action in screen_share_actions + recording_actions + breakout_actions:
            # For screen share and recording actions, we might want to send to everyone, including sender
            # or handle specific WebRTC signaling. For now, following the existing logic.
            await self.send(text_data=json.dumps({
                'action': action,
                'data': data,
                'sender': sender
            }))


