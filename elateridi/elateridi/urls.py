from django.urls import path
from elateridi import views
from elateridi import tasks

urlpatterns = [
    path('elateridi/', tasks.elateridi_list),
    path('elateridi/<int:pk>/', tasks.elateridi_detail),
]
