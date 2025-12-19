from django.urls import path
from pseudoperonospora import views
from pseudoperonospora import tasks

urlpatterns = [
    # path('pseudoperonospora/', views.pseudoperonospora_list),
    # path('pseudoperonospora/<int:pk>/', views.pseudoperonospora_detail),
    path('pseudoperonospora/', tasks.pseudoperonospora_list),
    path('pseudoperonospora/<int:pk>/', tasks.pseudoperonospora_detail),
]

#urlpatterns = format_suffix_patterns(urlpatterns)
