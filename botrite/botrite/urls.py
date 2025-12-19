from django.urls import path
from botrite import views
from botrite import tasks

urlpatterns = [
    # path('botrite/', views.botrite_list),
    # path('botrite/<int:pk>/', views.botrite_detail),
    path('botrite/', tasks.botrite_list),
    path('botrite/<int:pk>/', tasks.botrite_detail),
]

#urlpatterns = format_suffix_patterns(urlpatterns)