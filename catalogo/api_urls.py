from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from . import api_views

# El router genera las rutas de lista (/api/productos/) y detalle (/api/productos/<id>/)
router = DefaultRouter()
router.register('productos', api_views.ProductoViewSet, basename='producto')
router.register('categorias', api_views.CategoriaViewSet, basename='categoria')

urlpatterns = [
    # POST con usuario y contraseña -> devuelve el token de acceso
    path('token/', obtain_auth_token, name='api-token'),
    path('', include(router.urls)),
]
