from django.contrib import admin
from .models import DiscussionThread, DiscussionPost, ForumReaction

class DiscussionPostInline(admin.StackedInline):
    model = DiscussionPost
    extra = 1

@admin.register(DiscussionThread)
class DiscussionThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'author', 'is_pinned', 'is_locked', 'view_count', 'created_at', 'updated_at')
    list_filter = ('course', 'is_pinned', 'is_locked', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    filter_horizontal = ('mentions',)
    inlines = [DiscussionPostInline]


@admin.register(DiscussionPost)
class DiscussionPostAdmin(admin.ModelAdmin):
    list_display = ('thread', 'author', 'is_solution', 'created_at')
    list_filter = ('is_solution', 'created_at')
    search_fields = ('content', 'author__username')
    filter_horizontal = ('mentions',)


@admin.register(ForumReaction)
class ForumReactionAdmin(admin.ModelAdmin):
    list_display = ('target_type', 'user', 'emoji', 'created_at')
    list_filter = ('target_type', 'emoji', 'created_at')
    search_fields = ('user__username',)
