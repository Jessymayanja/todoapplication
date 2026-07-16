from django.contrib import admin
from .models import CustomUser, Todo

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Todo)


