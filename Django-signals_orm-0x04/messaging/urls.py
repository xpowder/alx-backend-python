from django.urls import path
from .views import (
    delete_user,
    ThreadedConversationView,
    UnreadMessagesView
)

urlpatterns = [
    path('users/delete/', delete_user, name='delete-user'),
    path('thread/', ThreadedConversationView.as_view(), name='threaded-conversation'),
    path('messages/unread/', UnreadMessagesView.as_view(), name='unread-messages'),
]
