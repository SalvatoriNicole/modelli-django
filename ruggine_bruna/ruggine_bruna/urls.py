from django.urls import path
from ruggine_bruna import views
from ruggine_bruna import tasks

urlpatterns = [
    path('ruggine_bruna/', tasks.ruggine_bruna_list),
    path('ruggine_bruna/<int:pk>/', tasks.ruggine_bruna_detail),
]
