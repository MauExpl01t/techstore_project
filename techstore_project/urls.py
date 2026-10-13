"""URL configuration for techstore_project project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from catalogo.forms import LoginForm

urlpatterns = [
    path('admin/', admin.site.urls),
    # Autenticación con django.contrib.auth
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=LoginForm,
        redirect_authenticated_user=True,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # API REST (Django REST Framework)
    path('api/', include('catalogo.api_urls')),
    path('', include('catalogo.urls')),
]

# En desarrollo (DEBUG=True) Django sirve las fotos subidas desde /media/
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
