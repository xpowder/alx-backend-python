from rest_framework import serializers
from .models import Message, Notification, MessageHistory


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'sender_username', 'receiver', 'receiver_username',
            'content', 'timestamp', 'edited', 'is_read', 'parent_message'
        ]
        read_only_fields = ['id', 'timestamp', 'edited']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    message = MessageSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class MessageHistorySerializer(serializers.ModelSerializer):
    """Serializer for MessageHistory model."""
    
    class Meta:
        model = MessageHistory
        fields = ['id', 'message', 'old_content', 'edited_at']
        read_only_fields = ['id', 'edited_at']

