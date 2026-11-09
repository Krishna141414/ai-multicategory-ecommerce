"""Queries between customers and the admin, stored in one messages table (brief rule 6).

- A new conversation gets a fresh conversation_id and parent_message = NULL.
- A reply points at the message it answers and reuses its conversation_id.
- Customers only ever see conversations they take part in; the admin sees all.
"""

import secrets
from dataclasses import dataclass
from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Max, Q

from accounts.services import default_admin
from messaging.models import Message, Role


def role_of(user: User) -> str:
    return Role.ADMIN if user.is_staff else Role.CUSTOMER


def new_conversation_id() -> str:
    """A short, unique id such as CNV-7F3A92C1."""
    while True:
        candidate = f"CNV-{secrets.token_hex(4).upper()}"
        if not Message.objects.filter(conversation_id=candidate).exists():
            return candidate


@transaction.atomic
def start_conversation(sender: User, receiver: User, subject: str, message: str) -> Message:
    """Brief: Post Query. Starts a new conversation (parent_message_id = NULL)."""
    return Message.objects.create(
        conversation_id=new_conversation_id(), sender=sender, sender_type=role_of(sender),
        receiver=receiver, receiver_type=role_of(receiver), parent_message=None,
        subject=subject.strip(), message=message.strip(),
    )


def start_customer_query(customer_user: User, subject: str, message: str) -> Message:
    """A customer's new query goes to the store admin."""
    admin = default_admin()
    if admin is None:
        raise ValueError("No admin account exists to receive the query.")
    return start_conversation(customer_user, admin, subject, message)


@transaction.atomic
def reply(conversation_id: str, sender: User, message: str) -> Message:
    """Brief: Reply Query. Answers the latest message in the thread and keeps the conversation_id."""
    thread_messages = list(Message.objects.filter(conversation_id=conversation_id).order_by("posted_date", "id"))
    if not thread_messages:
        raise Message.DoesNotExist(conversation_id)
    ensure_can_view(sender, thread_messages)
    parent = thread_messages[-1]
    first = thread_messages[0]
    # the other party: for a customer it is always the admin; for the admin it is the customer
    customer = first.sender if first.sender_type == Role.CUSTOMER else first.receiver
    receiver = default_admin() if not sender.is_staff else customer
    if receiver is None:
        raise ValueError("No admin account exists to receive the reply.")
    subject = first.subject if first.subject.lower().startswith("re:") else f"Re: {first.subject}"
    return Message.objects.create(
        conversation_id=conversation_id, sender=sender, sender_type=role_of(sender), receiver=receiver,
        receiver_type=role_of(receiver), parent_message=parent, subject=subject, message=message.strip(),
    )


def ensure_can_view(user: User, thread_messages: list[Message]) -> None:
    """Customers may only open conversations they are part of (brief rule 6)."""
    if user.is_staff:
        return
    if not any(m.sender_id == user.id or m.receiver_id == user.id for m in thread_messages):
        raise PermissionDenied("This conversation belongs to another customer.")


def thread(conversation_id: str, user: User) -> list[Message]:
    """All messages of a conversation in order, after the access check."""
    thread_messages = list(Message.objects.filter(conversation_id=conversation_id)
                           .select_related("sender", "receiver", "parent_message").order_by("posted_date", "id"))
    if not thread_messages:
        raise Message.DoesNotExist(conversation_id)
    ensure_can_view(user, thread_messages)
    return thread_messages


def mark_read(conversation_id: str, user: User) -> int:
    """Mark messages addressed to this user (or, for the admin, to any admin) as read."""
    qs = Message.objects.filter(conversation_id=conversation_id, status=Message.Status.UNREAD)
    qs = qs.filter(receiver_type=Role.ADMIN) if user.is_staff else qs.filter(receiver=user)
    return qs.update(status=Message.Status.READ)


@dataclass
class ConversationSummary:
    conversation_id: str
    subject: str
    customer_name: str
    customer_email: str
    last_message: str
    last_sender_type: str
    last_posted: datetime
    message_count: int
    unread: int


def conversations_for(user: User, search: str = "") -> list[ConversationSummary]:
    """Brief: View Queries. Customers get their own conversations; the admin gets all of them."""
    qs = Message.objects.all()
    if not user.is_staff:
        qs = qs.filter(Q(sender=user) | Q(receiver=user))
    unread_filter = Q(status=Message.Status.UNREAD) & (Q(receiver_type=Role.ADMIN) if user.is_staff else Q(receiver=user))
    groups = (qs.values("conversation_id")
              .annotate(last_posted=Max("posted_date"), message_count=Count("id"), unread=Count("id", filter=unread_filter))
              .order_by("-last_posted"))
    summaries = []
    for g in groups:
        msgs = Message.objects.filter(conversation_id=g["conversation_id"]).select_related("sender__customer", "receiver__customer").order_by("posted_date", "id")
        first, last = msgs.first(), msgs.last()
        customer_user = first.sender if first.sender_type == Role.CUSTOMER else first.receiver
        customer = getattr(customer_user, "customer", None)
        name = customer.name if customer else customer_user.get_username()
        email = customer.email if customer else customer_user.email
        if search and search.lower() not in f"{first.subject} {name} {email} {g['conversation_id']}".lower():
            continue
        summaries.append(ConversationSummary(
            conversation_id=g["conversation_id"], subject=first.subject, customer_name=name, customer_email=email,
            last_message=last.message, last_sender_type=last.sender_type, last_posted=g["last_posted"],
            message_count=g["message_count"], unread=g["unread"],
        ))
    return summaries
