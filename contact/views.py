from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import ContactMessage
from .serializers import ContactMessageSerializer
from rest_framework import generics, filters


# عرض وإضافة الرسائل
class ContactMessageListView(generics.ListCreateAPIView):
    queryset = ContactMessage.objects.all().order_by('-created_at')
    serializer_class = ContactMessageSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'email', 'purpose', 'message']

    def get_permissions(self):
        if self.request.method == 'POST':
            return []  # أي حد يقدر يبعت رسالة
        return [IsAuthenticated()]  # القراءة للـ admin بس