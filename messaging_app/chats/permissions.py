#messaging_app/chats/permissions.py
from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
            if hasattr(obj, "participants"):
                return request.user in obj.participants.all()
            elif hasattr(obj, "conversation"):
                return request.user in obj.conversation.participants.all()
        return False
