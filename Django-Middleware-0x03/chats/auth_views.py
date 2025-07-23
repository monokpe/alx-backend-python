from rest_framework_simplejwt.views import TokenObtainPairView
from .auth import MyTokenObtainPairSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    """
    Handles POST requests with user credentials (email, password) and returns
    an access and refresh JSON web token pair.
    """
    serializer_class = MyTokenObtainPairSerializer