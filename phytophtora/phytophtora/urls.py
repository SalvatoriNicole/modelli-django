from django.urls import path
from phytophtora import views
from phytophtora import tasks

urlpatterns = [
    path('phytophtora/', tasks.phytophtora_list),
    path('phytophtora/<int:pk>/', tasks.phytophtora_detail),
]
