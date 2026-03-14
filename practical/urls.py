from django.urls import path
from . import views

app_name = 'practical'

urlpatterns = [
    path('', views.assignment_list, name='list'),
    path('<int:pk>/', views.assignment_detail, name='detail'),
]