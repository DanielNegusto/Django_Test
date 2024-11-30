import random
import string
from django.db import models


class User(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    verification_code = models.CharField(max_length=4, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    invite_code = models.CharField(max_length=6, unique=True, blank=True, null=True)
    activated_users = models.ManyToManyField(
        "self", symmetrical=False, related_name="invited_by", blank=True
    )

    activated_invite_code = models.BooleanField(default=False)

    def generate_invite_code(self):
        """Генерация случайного 6-значного инвайт-кода из цифр и букв."""
        characters = string.ascii_letters + string.digits
        self.invite_code = "".join(random.choice(characters) for _ in range(6))

    def __str__(self):
        return self.phone_number
