from django.urls import path
from .views import (
    RegisterView,
    TodoListView,
    TodoDetailView,
    TodoCreateView,
    TodoDeleteView,
    TodoUpdateView,
    VerifyEmailView
)
urlpatterns = [
    path("", TodoListView.as_view(), name="todo-list"),
    path("create/", TodoCreateView.as_view(), name="todo-create"),
    path("<int:pk>/", TodoDetailView.as_view(), name="todo-detail"),
    path("<int:pk>/update/", TodoUpdateView.as_view(), name="todo-update"),
    path("<int:pk>/delete/", TodoDeleteView.as_view(), name="todo-delete"),
    path("verify-email/<str:uidb64>/<str:token>/", VerifyEmailView.as_view()),
]

