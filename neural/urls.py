from django.urls import path
from . import views

app_name = 'neural'

urlpatterns = [
    path('', views.path_list, name='path_list'),
    path('element/<int:element_id>/', views.element_detail, name='element_detail'),
]