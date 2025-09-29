from rest_framework import permissions
from .models import Conversation


class IsParticipantOfConversation(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()

        if hasattr(obj, "conversation"):
            return request.user in obj.conversation.participants.all()

        return False
