from django.db.models import ProtectedError
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Categoria, Producto
from .serializers import CategoriaSerializer, ProductoSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    """API REST de productos.

    Públicos (lectura):
        GET    /api/productos/        lista de productos
        GET    /api/productos/<id>/   detalle de un producto
    Privados (requieren cabecera  Authorization: Token <clave>):
        POST   /api/productos/        crear
        PUT    /api/productos/<id>/   edición total
        PATCH  /api/productos/<id>/   edición parcial
        DELETE /api/productos/<id>/   eliminar
    """

    queryset = Producto.objects.select_related('categoria')
    serializer_class = ProductoSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]


class CategoriaViewSet(viewsets.ModelViewSet):
    """API REST de categorías, con las mismas reglas de acceso que los productos."""

    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        # La relación usa on_delete=PROTECT: no se borra una categoría con productos
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {'detail': 'No se puede eliminar la categoría porque tiene productos asociados.'},
                status=status.HTTP_409_CONFLICT,
            )
