from django.urls import path
from . import views

urlpatterns = [
    path('review/delete/<int:pk>/', views.delete_review, name='delete_review'),
]