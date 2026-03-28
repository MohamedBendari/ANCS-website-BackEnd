from django.db import models

# Create your models here.

class ContactMessage(models.Model):

    PURPOSE_CHOICES = [
        ('buy', 'Buy ANCS'),
        ('support', 'Technical Support'),
        ('question', 'General Question'),
        ('partnership', 'Partnership'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  

    def __str__(self):
        return self.name