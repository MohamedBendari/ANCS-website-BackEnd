from django.urls import path
from .views import ContactMessageListView, DeleteMessageView

urlpatterns = [
    path('messages/', ContactMessageListView.as_view(), name='messages'),

    path(
        'messages/<int:message_id>/delete/',
        DeleteMessageView.as_view(),
        name='delete-message'
    ),
]   