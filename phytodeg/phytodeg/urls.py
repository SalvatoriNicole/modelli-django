from django.urls import path
from phytodeg import views
from phytodeg import tasks

urlpatterns = [
    path('phytodeg/', tasks.phytodeg_list),
    path('phytodeg/<int:pk>/', tasks.phytodeg_detail),
]
