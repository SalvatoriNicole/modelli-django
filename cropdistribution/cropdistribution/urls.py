from django.urls import path
from cropdistribution import views
from cropdistribution import tasks

urlpatterns = [
    # path('botrite/', views.botrite_list),
    # path('botrite/<int:pk>/', views.botrite_detail),
    path('cropdistribution/', tasks.cropdistribution_list),
    path('cropdistribution/<int:pk>/', tasks.cropdistribution_detail),
]

#urlpatterns = format_suffix_patterns(urlpatterns)
