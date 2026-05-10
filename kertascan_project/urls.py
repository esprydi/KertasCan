# pyrefly: ignore [missing-import]
from django.contrib import admin
# pyrefly: ignore [missing-import]
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ocr_app.urls')),
]
