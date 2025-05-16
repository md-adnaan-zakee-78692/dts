from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('A', 'User A'),
        ('B', 'User B'),
        ('C', 'User C'),
        ('D', 'User D'),
        ('E', 'User E'),
    ]
    role = models.CharField(max_length=1, choices=ROLE_CHOICES)

class Document(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_by = models.ForeignKey(CustomUser, related_name='created_documents', on_delete=models.CASCADE)
    current_handler = models.ForeignKey(CustomUser, related_name='handling_documents', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('REJECTED', 'Rejected'),
        ('APPROVED', 'Approved'),
        ('COMPLETED', 'Completed'),
    ], default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    serial_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    last_approved_by = models.ForeignKey(
        CustomUser, null=True, blank=True, related_name='last_approver',
        on_delete=models.SET_NULL
    )
    def formatted_doc_id(self):
        return f"{self.created_at.strftime('%d%m%Y')}-{self.serial_number}"

class DocumentAction(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='actions')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=[('APPROVE', 'Approve'), ('REJECT', 'Reject')])
    comment = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
