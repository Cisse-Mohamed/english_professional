from django.contrib import admin
from .models import VideoSession

@admin.register(VideoSession)
class VideoSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'start_time', 'end_time')
    list_filter = ('course', 'start_time')
    search_fields = ('title', 'course__title')
