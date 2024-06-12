from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailCaseInsensitiveBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Case insensitive lookup for email
            user = UserModel.objects.get(email__iexact=username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None