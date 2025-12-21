from django.contrib import admin
from .models import VideoSession, BreakoutRoom, VideoSessionParticipant, VideoRecording

@admin.register(VideoSession)
class VideoSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'start_time', 'end_time')
    list_filter = ('course', 'start_time')
    search_fields = ('title', 'course__title')

@admin.register(BreakoutRoom)
class BreakoutRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'session', 'is_active', 'created_at')
    list_filter = ('session', 'is_active')
    search_fields = ('name', 'session__title')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(VideoSessionParticipant)
class VideoSessionParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'breakout_room', 'joined_at', 'left_at', 'is_host')
    list_filter = ('session', 'is_host', 'breakout_room')
    search_fields = ('user__username', 'session__title')
    raw_id_fields = ('user', 'session', 'breakout_room')

@admin.register(VideoRecording)
class VideoRecordingAdmin(admin.ModelAdmin):
    list_display = ('session', 'recorded_by', 'start_time', 'end_time', 'file_url')
    list_filter = ('session', 'recorded_by')
    search_fields = ('session__title', 'recorded_by__username')

