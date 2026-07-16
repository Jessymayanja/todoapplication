from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, Todo
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone

class CustomUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, allow_blank=False)
    email = serializers.EmailField(required=True, allow_blank=False)
    phone = serializers.RegexField(
        regex=r"^\+\d{9,15}$",
        error_messages={
            "invalid": "Phone number must include a country code and start with '+' followed by 9 to 15 digits."
        },
        required=True,
        allow_blank=False,
        max_length=16,
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        required=True
    )

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "password",
        ]

    # Username validation
    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "This username is already taken."
            )
        return value

    # Email validation
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
        return value

    # Password validation
    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)

        return value

    # Phone validation
    def validate_phone(self, value):
        if CustomUser.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "A user with this phone number already exists."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()

        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        return data

class TodoSerializer(serializers.ModelSerializer):
    is_overdue = serializers.ReadOnlyField()
    is_complete = serializers.ReadOnlyField()

    class Meta:
        model = Todo
        fields = [
            "id",
            "user",
            "description",
            "created_at",
            "deadline",
            "completion",
            "is_overdue",
            "is_complete",
        ]
        read_only_fields = [
            "user",
            "created_at",
            "is_overdue",
            "is_complete",
        ]



    def validate_deadline(self, deadline):
        if deadline < timezone.now():
            raise serializers.ValidationError(
                "Deadline cannot be in the past."
            )
        return deadline