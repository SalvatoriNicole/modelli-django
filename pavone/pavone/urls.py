from django.urls import path
from pavone import views
from pavone import tasks

urlpatterns = [
    path('pavone/', tasks.pavone_list),
    path('pavone/<int:pk>/', tasks.pavone_detail),
]
