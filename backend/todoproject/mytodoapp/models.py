from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=16, blank=True, null=True)
    is_verified = models.BooleanField(default=False)


class Todo(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="todos",
    )
    description = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    completion = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)
    final_reminder_sent = models.BooleanField(default=False)

    @property
    def is_overdue(self):
        return self.deadline < timezone.now() and not self.completion

    @property
    def is_complete(self):
        return self.completion

    def __str__(self):
        return f"{self.description} (user={self.user_id})"