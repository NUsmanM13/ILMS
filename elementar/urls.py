from django.urls import path
from . import views

app_name = 'elementar'

urlpatterns = [
    path('lessons/', views.lesson_list, name='lesson_list'),
    path('element/<int:element_id>/', views.element_detail, name='element_detail'),
]