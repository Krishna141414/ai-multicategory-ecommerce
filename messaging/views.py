"""Brief: Post Query, View Queries, Reply Query, View Conversation History (customer side).

Customers only see conversations they take part in; `services.thread` enforces that.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render

from core.permissions import customer_required
from messaging import services
from messaging.forms import QueryForm, ReplyForm
from messaging.models import Message


@customer_required
def query_list(request):
    """Brief: View Queries (own conversations, newest activity first)."""
    return render(request, "messaging/list.html", {"conversations": services.conversations_for(request.user)})


@customer_required
def query_new(request):
    """Brief: Post Query. Starts a new conversation with the store (parent_message_id = NULL)."""
    initial = {"subject": request.GET.get("subject", "")[:150]}
    form = QueryForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        try:
            message = services.start_customer_query(request.user, form.cleaned_data["subject"], form.cleaned_data["message"])
        except ValueError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, "Your query is sent. We'll reply here.")
            return redirect("messaging:thread", conversation_id=message.conversation_id)
    return render(request, "messaging/new.html", {"form": form})


@customer_required
def query_thread(request, conversation_id: str):
    """Brief: View Conversation History + Reply Query."""
    try:
        thread = services.thread(conversation_id, request.user)
    except Message.DoesNotExist:
        raise Http404("Conversation not found")
    form = ReplyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        services.reply(conversation_id, request.user, form.cleaned_data["message"])
        messages.success(request, "Reply sent.")
        return redirect("messaging:thread", conversation_id=conversation_id)
    services.mark_read(conversation_id, request.user)
    return render(request, "messaging/thread.html", {
        "thread": thread, "conversation_id": conversation_id, "subject": thread[0].subject, "form": form,
    })
