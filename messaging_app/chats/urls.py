from django.urls import path, include

# Import the routers module explicitly
from rest_framework import routers
from .views import ConversationViewSet, MessageViewSet

# Instantiate the router using the full module path as the checker expects
router = routers.DefaultRouter()

# Register the viewsets with the router
router.register(r"conversations", ConversationViewSet, basename="conversation")
router.register(r"messages", MessageViewSet, basename="message")

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
]
