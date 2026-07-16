from django.contrib import admin
from django.urls import path, include
from mytodoapp.views import RegisterView, CustomTokenObtainPairView

# Jwt tokens
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    #for rest framework
    path("api-auth/", include("rest_framework.urls")),
    # for jwt
    path("api/token/", CustomTokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),
    path("api/register/", RegisterView.as_view()),
    path("todos/", include('mytodoapp.urls'))
]


