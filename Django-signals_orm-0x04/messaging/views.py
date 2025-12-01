from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from .models import Message
from .serializers import MessageSerializer

User = get_user_model()


# Task 3: View for threaded conversations with optimized ORM queries
class ThreadedConversationView(ListAPIView):
    """
    A view to demonstrate efficient fetching of a threaded conversation.
    Uses select_related and prefetch_related to optimize database queries.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Fetches top-level messages (messages without a parent) for the authenticated user.
        Uses select_related for foreign key optimization and prefetch_related
        for reverse foreign key (replies) optimization.
        """
        queryset = Message.objects.filter(
            receiver=self.request.user,
            parent_message__isnull=True
        ).select_related('sender').prefetch_related('replies')
        
        return queryset

    def post(self, request, *args, **kwargs):
        """
        Creates a new message. Can be used to create a reply by providing
        a parent_message_id in the request data.
        """
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(sender=request.user)
            return Response(
                MessageSerializer(message).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Task 2: View to delete user account
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_user(request):
    """
    A view that allows an authenticated user to delete their own account.
    The post_delete signal will automatically clean up related data.
    """
    user = request.user
    user.delete()
    return Response(
        {"message": "User account deleted successfully"},
        status=status.HTTP_204_NO_CONTENT
    )


# Task 4: View to display unread messages using custom manager
class UnreadMessagesView(ListAPIView):
    """
    API view to display a list of unread messages for the
    authenticated user, using the custom ORM manager.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Use the custom manager to get unread messages for the user.
        Apply .only() optimization to retrieve only necessary fields.
        """
        queryset = Message.unread.unread_for_user(
            self.request.user
        ).only('id', 'sender', 'content', 'timestamp', 'is_read')
        
        return queryset
