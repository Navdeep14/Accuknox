# api/views.py
from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import User, FriendRequest
from .serializers import UserSerializer, RegisterSerializer, FriendRequestSerializer
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from datetime import timedelta

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            return Response({"token": user.auth_token.key})
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        if '@' in query:
            return User.objects.filter(email__iexact=query)
        return User.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query))

class FriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        to_user = User.objects.get(id=user_id)
        if FriendRequest.objects.filter(from_user=request.user, to_user=to_user, status='pending').exists():
            return Response({"error": "Friend request already sent"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Rate limiting: no more than 3 requests per minute
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        if FriendRequest.objects.filter(from_user=request.user, created_at__gte=one_minute_ago).count() >= 3:
            return Response({"error": "Too many requests. Please wait a minute."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        friend_request = FriendRequest.objects.create(from_user=request.user, to_user=to_user)
        return Response(FriendRequestSerializer(friend_request).data)

    def put(self, request, request_id):
        friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
        action = request.data.get('action')
        if action not in ['accept', 'reject']:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        
        friend_request.status = 'accepted' if action == 'accept' else 'rejected'
        friend_request.save()
        return Response(FriendRequestSerializer(friend_request).data)

class FriendListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.request.user.friends.filter(friendship__status='accepted')

class PendingRequestsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        return self.request.user.received_requests.filter(status='pending')
