from django.urls import path
from blackrot import views
from blackrot import tasks

urlpatterns = [
    path('blackrot/', tasks.blackrot_list),
    path('blackrot/<int:pk>/', tasks.blackrot_detail),
]