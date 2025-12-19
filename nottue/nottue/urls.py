from django.urls import path
from nottue import views
from nottue import tasks

urlpatterns = [
    path('nottue/', tasks.nottue_list),
    path('nottue/<int:pk>/', tasks.nottue_detail),
]
