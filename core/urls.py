from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'), # JS dagi xato bermasligi uchun
    path('export/docx/', views.export_results_docx, name='export_docx'),
    path('certificate/', views.view_certificate, name='certificate'),
]