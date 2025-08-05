from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .models import Message


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
