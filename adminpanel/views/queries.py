"""Brief: View Queries, Post Query, Reply Query, View Conversation History (admin side)."""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render

from adminpanel.views.common import paginate
from core.permissions import admin_required
from messaging import services
from messaging.forms import AdminQueryForm, ReplyForm
from messaging.models import Message, Role


@admin_required
def query_inbox(request):
    q = request.GET.get("q", "").strip()
    conversations = services.conversations_for(request.user, search=q)
    return render(request, "adminpanel/queries/inbox.html", {
        "section": "queries", "page": paginate(request, conversations), "q": q,
        "unread_total": sum(c.unread for c in conversations),
    })


@admin_required
def query_new(request):
    initial = {"customer": request.GET.get("customer")} if request.GET.get("customer") else None
    form = AdminQueryForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        customer = form.cleaned_data["customer"]
        message = services.start_conversation(request.user, customer.user, form.cleaned_data["subject"],
                                              form.cleaned_data["message"])
        messages.success(request, f"Query sent to {customer.name}.")
        return redirect("adminpanel:query_thread", conversation_id=message.conversation_id)
    return render(request, "adminpanel/queries/new.html", {"section": "queries", "form": form})


@admin_required
def query_thread(request, conversation_id):
    try:
        thread = services.thread(conversation_id, request.user)
    except Message.DoesNotExist:
        raise Http404("Conversation not found")
    form = ReplyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        services.reply(conversation_id, request.user, form.cleaned_data["message"])
        messages.success(request, "Reply sent.")
        return redirect("adminpanel:query_thread", conversation_id=conversation_id)
    services.mark_read(conversation_id, request.user)
    first = thread[0]
    customer_user = first.sender if first.sender_type == Role.CUSTOMER else first.receiver
    return render(request, "adminpanel/queries/thread.html", {
        "section": "queries", "thread": thread, "conversation_id": conversation_id, "form": form,
        "subject": first.subject, "customer": getattr(customer_user, "customer", None),
    })
