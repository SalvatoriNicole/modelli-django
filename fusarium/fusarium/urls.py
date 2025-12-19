from django.urls import path
from fusarium import views
from fusarium import tasks

urlpatterns = [
    # path('fusarium/', views.fusarium_list),
    # path('fusarium/<int:pk>/', views.fusarium_detail),
    path('fusarium/', tasks.fusarium_list),
    path('fusarium/<int:pk>/', tasks.fusarium_detail),
]

#urlpatterns = format_suffix_patterns(urlpatterns)
