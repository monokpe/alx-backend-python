from django.urls import path, include
from rest_framework_nested import routers
from .views import ConversationViewSet, MessageViewSet

router = routers.SimpleRouter()
router.register(r"conversations", ConversationViewSet, basename="conversation")

# Create a nested router for the child resource (Messages)
conversations_router = routers.NestedDefaultRouter(
    router, r"conversations", lookup="conversation"
)
conversations_router.register(
    r"messages", MessageViewSet, basename="conversation-messages"
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(conversations_router.urls)),
]
