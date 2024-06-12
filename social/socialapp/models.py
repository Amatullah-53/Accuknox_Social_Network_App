from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.contrib.auth.models import User

class FriendRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined')
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')


# class Login(models.Model):
#     email = models.CharField(max_length=100, unique=True)
#     password = models.CharField(max_length=100)
#     last_login = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         db_table = "login"

#     def __str__(self):
#         return self.email

#     def set_password(self, raw_password):
#         self.password = make_password(raw_password)
#         self.save()

#     def check_password(self, raw_password):
#         return check_password(raw_password, self.password)

#     def update_last_login(self):
#         self.last_login = timezone.now()
#         self.save()