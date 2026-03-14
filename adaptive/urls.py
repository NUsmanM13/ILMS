from django.urls import path
from . import views

app_name = 'adaptive'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('element/<int:element_id>/', views.element_detail, name='element_detail'),
]