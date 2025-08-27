from django.urls import path
from .views import react_register, react_login, react_logout, check_auth, ask_ai

urlpatterns = [
    path('react-register/', react_register),
    path('react-login/', react_login),
    path('react-logout/', react_logout),
    path('check-auth/', check_auth),
     path('ask-ai/', ask_ai),
]
