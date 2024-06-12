
from . import views
from django.urls import path
from .views import send_friend_request, add_friends


urlpatterns = [
    path('home',views.home),
    path('login',views.user_login),
    path('signup',views.signup),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.home, name='home'), 
    path('pending_friend_requests/', views.pending_friend_requests),
    path('notifications',views.notifications),
    path('update_friend_request_status/<int:request_id>/<str:status>/', views.update_friend_request_status, name='update_friend_request_status'),
    path('search_users',views.search_users),
    path('unfriend/<int:user_id>/', views.unfriend, name='unfriend'),
    path('logout/', views.logout_view),
    path('my-friends/', views.my_friends),
    path('send_friend_request/<int:receiver_id>/', send_friend_request, name='send_friend_request'),
    path('add_friends/', add_friends, name='add_friends'),
]
   
