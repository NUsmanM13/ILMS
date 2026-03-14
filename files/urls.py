from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    path('', views.folder_list, name='list'),
    path('folder/<int:pk>/', views.folder_detail, name='detail'),
]