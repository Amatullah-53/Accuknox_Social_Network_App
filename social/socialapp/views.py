from django.shortcuts import render, redirect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, LoginSerializer
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm, LoginForm
from django.core.paginator import Paginator
from django.shortcuts import HttpResponse
from .models import FriendRequest
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from .models import User
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })

# Create your views here.
def home(request):
    return render(request, "home.html")

@login_required
def dashboard(request):
    user = request.user
    context = {
        'username': user.username,
        'email': user.email,
        # Add any other user fields you want to display
    }
    return render(request, 'dashboard.html', context)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'invalid.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to dashboard
    else:
        form = LoginForm()
    return render(request, 'home.html', {'form': form})

@login_required
def add_friends(request):
    # Fetch all users except the logged-in user
    users = User.objects.exclude(id=request.user.id)
    
    # Pagination: 10 users per page
    paginator = Paginator(users, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Iterate through each user in the page_obj
    for user in page_obj:
        # Check if there exists a friend request between the logged-in user and the current user
        friend_request = FriendRequest.objects.filter(
            Q(sender=request.user, receiver=user) | Q(sender=user, receiver=request.user)
        ).first()
        # If a friend request exists, fetch its status. Otherwise, set the status to None
        user.friend_request_status = friend_request.status if friend_request else None

    context = {
        'username': request.user.username,
        'email': request.user.email,
        'page_obj': page_obj,
    }

    return render(request, 'makefriends.html', context)

    



@login_required
def send_friend_request(request, receiver_id):
    receiver = User.objects.get(id=receiver_id)

    # Check for rate limiting
    one_minute_ago = timezone.now() - timedelta(minutes=1)
    recent_requests_count = FriendRequest.objects.filter(sender=request.user, created_at__gte=one_minute_ago).count()

    if recent_requests_count >= 3:
        messages.error(request, 'Please wait a few seconds. You can only send 3 friend requests in one minute.')
        return redirect('add_friends')

    # Check if a friend request already exists
    existing_request = FriendRequest.objects.filter(sender=request.user, receiver=receiver).first()
    if existing_request:
        # If a request already exists, update the status to 'pending'
        existing_request.status = 'pending'
        existing_request.save()
    else:
        # If no request exists, create a new one with status 'pending'
        FriendRequest.objects.create(sender=request.user, receiver=receiver, status='pending')

    return redirect('add_friends')  # Redirect to the add friends page or any other page you want




@login_required
def search_users(request):
    search_term = request.GET.get("search", None)
    all_users = User.objects.exclude(id=request.user.id)  # Exclude the logged-in user
    users_list = [user for user in all_users]

    qs = User.objects.all()
    if search_term is not None:
        qs = qs.filter(Q(username__icontains=search_term) | Q(email__icontains=search_term))

    filtered_users = []
    for user in qs:
        if user in users_list:
            filtered_users.append(user)

    # Pagination: 10 users per page
    paginator = Paginator(filtered_users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'username': request.user.username,
        'users': qs,
        'email': request.user.email,
        'page_obj': page_obj,
        'search_term': search_term,  # Pass the search term to the template
    }

    template = "search_users.html"
    return render(request, template, context)



@login_required
def pending_friend_requests(request):
    user = request.user
    pending_requests = FriendRequest.objects.filter(sender=user, status='pending')
    context = {
        'username': request.user.username,
        'email': request.user.email,
        'pending_requests': pending_requests
    }
    return render(request, 'pendingrequest.html', context)

@login_required
def notifications(request):
    pending_requests = FriendRequest.objects.filter(receiver=request.user, status='pending')
    
    context = {
        'username': request.user.username,
        'email': request.user.email,
        'pending_requests': pending_requests,
    }
    return render(request, 'notifications.html', context)

@login_required
def update_friend_request_status(request, request_id, status):
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    if status == 'accepted':
        friend_request.status = 'accepted'
        friend_request.save()
        # Send notification to the sender

        messages.success(request, 'Friend request accepted successfully.')
    elif status == 'declined':
        friend_request.status = 'declined'
        friend_request.save()
        # Send notification to the sender
       
        messages.success(request, 'Friend request declined successfully.')
    
    # Fetch pending friend requests
    pending_requests = FriendRequest.objects.filter(receiver=request.user, status='pending')
    
    context = {
        'pending_requests': pending_requests,
    }
    
    return render(request, 'notifications.html', context)

@login_required
def unfriend(request, user_id):
    # Check if there exists a friend request where either the sender or receiver ID matches the current user's ID
    # and the other user's ID matches the user ID being unfriended, and the status is "accepted"
    friend_request = get_object_or_404(
        FriendRequest.objects.filter(
            (Q(sender=request.user, receiver_id=user_id, status='accepted') |
             Q(sender_id=user_id, receiver=request.user, status='accepted'))
        )
    )
    
    # Delete the friend request
    friend_request.delete()

    # Optionally, display a success message
    messages.success(request, 'You have unfriended this user.')
# Fetch all users except the logged-in user
    users = User.objects.exclude(id=request.user.id)
    
    # Pagination: 10 users per page
    paginator = Paginator(users, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Iterate through each user in the page_obj
    for user in page_obj:
        # Check if there exists a friend request between the logged-in user and the current user
        friend_request = FriendRequest.objects.filter(
            Q(sender=request.user, receiver=user) | Q(sender=user, receiver=request.user)
        ).first()
        # If a friend request exists, fetch its status. Otherwise, set the status to None
        user.friend_request_status = friend_request.status if friend_request else None

    context = {
        'username': request.user.username,
        'email': request.user.email,
        'page_obj': page_obj,
    }

    return render(request, 'makefriends.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def my_friends(request):
    user = request.user

    # Get all friend requests where the user is either the sender or receiver and the status is accepted
    friends = FriendRequest.objects.filter(
        (Q(sender=user) | Q(receiver=user)) & Q(status='accepted')
    )

    # Extract the friends from the friend requests
    friends_list = []
    for friend in friends:
        if friend.sender == user:
            friends_list.append(friend.receiver)
        else:
            friends_list.append(friend.sender)

    context = {
        'friends': friends_list,
        'username': request.user.username,
        'email': request.user.email,
    }
    return render(request, 'my_friends.html', context)

def can_send_request(user):
    one_minute_ago = datetime.now() - timedelta(minutes=1)
    requests_last_minute = FriendRequest.objects.filter(sender=user, created_at__gte=one_minute_ago).count()
    return requests_last_minute < 3





    




