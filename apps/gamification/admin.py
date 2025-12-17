from django.contrib import admin
from .models import Badge, UserPoints, UserBadge

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'points_required', 'slug', 'created_at')
    list_filter = ('points_required', 'created_at')
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('points_required',)

@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_points', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('user__username', 'user__email')
    ordering = ('-total_points',)
    readonly_fields = ('updated_at',)

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'awarded_at')
    list_filter = ('badge', 'awarded_at')
    search_fields = ('user__username', 'badge__name')
    ordering = ('-awarded_at',)
    readonly_fields = ('awarded_at',)
