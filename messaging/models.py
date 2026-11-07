"""One messages table for queries and replies between admin and customers (brief rule 6).

Fields: id, conversation_id, sender_id, sender_type, receiver_id, receiver_type,
parent_message_id, subject, message, posted_date, status.
A new conversation has parent_message = NULL; replies point at the message they
answer and reuse its conversation_id.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone


class Role(models.TextChoices):
    ADMIN = "admin", "Admin"
    CUSTOMER = "customer", "Customer"


class Message(models.Model):
    class Status(models.TextChoices):
        UNREAD = "Unread", "Unread"
        READ = "Read", "Read"

    conversation_id = models.CharField(max_length=20, db_index=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    sender_type = models.CharField(max_length=10, choices=Role.choices)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages")
    receiver_type = models.CharField(max_length=10, choices=Role.choices)
    parent_message = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True, related_name="replies")
    subject = models.CharField(max_length=150)
    message = models.TextField()
    posted_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UNREAD)

    class Meta:
        ordering = ["posted_date", "id"]

    def __str__(self) -> str:
        return f"[{self.conversation_id}] {self.subject}"

    @property
    def is_conversation_start(self) -> bool:
        return self.parent_message_id is None
