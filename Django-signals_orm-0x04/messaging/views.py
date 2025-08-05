from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages


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
