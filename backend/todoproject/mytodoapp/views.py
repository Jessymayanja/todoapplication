from rest_framework import generics, status
from rest_framework.response import Response 
from .models import Todo, CustomUser
from .serializers import (
    TodoSerializer,
    CustomUserSerializer,
    CustomTokenObtainPairSerializer,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from rest_framework.permissions import BasePermission
from django.db.models import Case, When, Value, IntegerField
from django.utils import timezone
from .email_utils import send_email
from .tokens import email_verification_token
from django.shortcuts import redirect
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(is_verified=False)

        # Build a secure one-time verification link
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)
        link = f"https://tododojo.duckdns.org/todos/verify-email/{uid}/{token}/"

        send_email(
            to_email=user.email,
            subject="Verify your Todo App account",
            html_content=(
                f"<p>Hi {user.username},</p>"
                f"<p>Click the link below to verify your account:</p>"
                f"<p><a href='{link}'>Verify my email</a></p>"
                f"<p>This link expires once used.</p>"
            ),
        )
        return Response(
            {
                "success": True,
                "message": "Your account has been successfully created. Please check your email to verify your account before logging in.",
                "email": user.email,
            },
            status=201,
        )

class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def _verify_user(self, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, CustomUser.DoesNotExist):
            return None

        if user and user.is_verified:
            return None

        if user and email_verification_token.check_token(user, token):
            user.is_verified = True
            user.save(update_fields=["is_verified"])
            return user

        return None

    def get(self, request, uidb64, token):
        user = self._verify_user(uidb64, token)
        if user:
            return redirect("https://todoappwe.netlify.app/login")

        return Response(
            {"error": "Invalid or expired verification link."},
            status=400
        )

    def post(self, request, uidb64, token):
        user = self._verify_user(uidb64, token)
        if user:
            return Response(
                {
                    "success": True,
                    "message": "Your email has been verified successfully.",
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Invalid or expired verification link."},
            status=status.HTTP_400_BAD_REQUEST,
        )
        
    
class IsVerified(BasePermission):
    message = "Please verify your email before accessing this resource."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_verified
    
# 1. Display all todos
class TodoListView(generics.ListAPIView):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated, IsVerified]

    def get_queryset(self):
        return (
            Todo.objects.filter(user=self.request.user)
            .annotate(
                overdue_flag=Case(
                    When(deadline__lt=timezone.now(), completion=False, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
            .order_by("overdue_flag", "deadline")
        )


# 2. Get todo by id
class TodoDetailView(generics.RetrieveAPIView):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated, IsVerified]


    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)


# 3. Add a todo
class TodoCreateView(generics.CreateAPIView):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated, IsVerified]


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Debug: log incoming content type, raw body and parsed data
        try:
            raw_body = request.body.decode("utf-8")
        except Exception:
            raw_body = "<unable to decode>"

        print("DEBUG TodoCreateView: content_type=", request.content_type)
        print("DEBUG TodoCreateView: raw_body=", raw_body)
        print("DEBUG TodoCreateView: request.data=", request.data)

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            # Log serializer errors and return them in the response
            err = getattr(e, "detail", str(e))
            print("DEBUG TodoCreateView: serializer errors=", err)
            return Response(err, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
   


# 4. Delete todo by id
class TodoDeleteView(generics.DestroyAPIView):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated, IsVerified]


    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)


# 5. Update todo by id
class TodoUpdateView(generics.UpdateAPIView):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated, IsVerified]


    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)