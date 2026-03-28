from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from .models import ContactMessage
from .serializers import ContactMessageSerializer

from rest_framework.permissions import AllowAny

class ContactMessageListView(generics.ListCreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]  # 👈 الحل هنا
# class ContactMessageListView(generics.ListAPIView):
#     queryset = ContactMessage.objects.all().order_by('-created_at')
#     serializer_class = ContactMessageSerializer

    # 🔐 حماية الـ API
    # permission_classes = [IsAuthenticated]

    # 🔍 Search + ترتيب
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['name', 'email', 'message']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']