from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .models import Message
from django.views.decorators.cache import cache_page


@login_required
def delete_user_account(request):
    """
    Allows a logged-in user to delete their own account.
    """
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been successfully deleted.")
        return redirect("home")
    return render(request, "messaging/delete_account_confirm.html")


def conversation_thread_view(request, conversation_id):
    """
    Displays a threaded conversation, optimized with prefetch_related and select_related.
    """
    top_level_messages = (
        Message.objects.filter(parent_message__isnull=True)
        .select_related("sender")
        .prefetch_related("replies")
    )

    context = {"messages": top_level_messages}
    return render(request, "chats/conversation_thread.html", context)


@login_required
def unread_messages_view(request):
    """
    Displays a list of unread messages for the logged-in user,
    using the custom manager and optimizing with .only().
    """

    unread_inbox = Message.unread.for_user(request.user).only(
        "id", "sender__username", "content", "timestamp"
    )

    context = {"unread_messages": unread_inbox}
    return render(request, "messaging/unread_inbox.html", context)


@cache_page(60)
def message_list_view(request):
    """
    A view that displays a list of all messages, cached for 60 seconds.
    """
    all_messages = Message.objects.all().select_related("sender", "receiver")

    context = {"messages": all_messages}
    return render(request, "chats/message_list.html", context)
