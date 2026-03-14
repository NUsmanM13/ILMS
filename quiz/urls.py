from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.exam_home, name='home'),
    path('start/<int:subject_id>/<str:exam_type>/', views.start_exam, name='start_exam'),
    path('take/<int:session_id>/', views.take_test, name='take_test'),
]