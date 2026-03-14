from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', core_views.login_view, name='login'),
    path('accounts/logout/', core_views.logout_view, name='logout'),
    path('', include('core.urls')),
    path('drive/', include('files.urls')),
    path('elementar/', include('elementar.urls')),
    path('adaptive/', include('adaptive.urls')),
    path('neural/', include('neural.urls')),
    path('quiz/', include('quiz.urls')),
    path('practical/', include('practical.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)