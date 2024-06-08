"""
URL configuration for social_network project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from api.views import RegisterView, LoginView, UserSearchView, FriendRequestView, FriendListView, PendingRequestsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('friend-request/<int:user_id>/', FriendRequestView.as_view(), name='send-friend-request'),
    path('friend-request/<int:request_id>/action/', FriendRequestView.as_view(), name='friend-request-action'),
    path('friends/', FriendListView.as_view(), name='friends-list'),
    path('pending-requests/', PendingRequestsView.as_view(), name='pending-requests'),
]
