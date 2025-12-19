from django.urls import path
from chooseplants import views
from chooseplants import tasks

urlpatterns = [
    # path('botrite/', views.botrite_list),
    # path('botrite/<int:pk>/', views.botrite_detail),
    path('chooseplants/', tasks.chooseplants_list),
    path('chooseplants/<int:pk>/', tasks.chooseplants_detail),
]

#urlpatterns = format_suffix_patterns(urlpatterns)
