from django.urls import path
from .views import ContactMessageListView

urlpatterns = [
    path('messages/', ContactMessageListView.as_view(), name='messages'),
]