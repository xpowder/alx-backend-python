from django.contrib import admin
from .models import Message, Notification, MessageHistory


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model."""
    list_display = ('id', 'sender', 'receiver', 'content', 'timestamp', 'edited', 'is_read', 'parent_message')
    list_filter = ('sender', 'receiver', 'edited', 'is_read', 'timestamp')
    search_fields = ('content', 'sender__username', 'receiver__username')
    readonly_fields = ('timestamp',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model."""
    list_display = ('id', 'user', 'message', 'is_read', 'created_at')
    list_filter = ('user', 'is_read', 'created_at')
    search_fields = ('user__username', 'message__content')
    readonly_fields = ('created_at',)


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    """Admin interface for MessageHistory model."""
    list_display = ('id', 'message', 'edited_at')
    list_filter = ('edited_at',)
    search_fields = ('message__content', 'old_content')
    readonly_fields = ('edited_at',)
