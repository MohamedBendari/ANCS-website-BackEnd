from django.contrib import admin
from .models import ContactMessage


# Register your models here.
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'purpose', 'created_at')
    search_fields = ('name', 'email', 'purpose')
    list_filter = ('purpose', 'created_at')
    ordering = ('-created_at',)

admin.site.register(ContactMessage, ContactMessageAdmin)

