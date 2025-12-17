from django.contrib import admin
from .models import Announcement, AnnouncementRead


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'scope', 'course', 'priority', 'is_pinned', 'created_at']
    list_filter = ['scope', 'priority', 'is_pinned', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'content', 'author')
        }),
        ('Scope & Targeting', {
            'fields': ('scope', 'course', 'priority')
        }),
        ('Settings', {
            'fields': ('send_email', 'is_pinned')
        }),
    )


@admin.register(AnnouncementRead)
class AnnouncementReadAdmin(admin.ModelAdmin):
    list_display = ['announcement', 'user', 'read_at']
    list_filter = ['read_at']
    search_fields = ['announcement__title', 'user__username']
    date_hierarchy = 'read_at'