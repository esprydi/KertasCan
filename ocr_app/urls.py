# pyrefly: ignore [missing-import]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('results/', views.results, name='results'),
    path('download/', views.download_excel, name='download_excel'),
    path('clear/', views.clear_session, name='clear_session'),
    path('edit/<int:index>/', views.edit_result, name='edit_result'),
]
