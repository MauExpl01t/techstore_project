from rest_framework import serializers

from .models import Categoria, Producto


class CategoriaSerializer(serializers.ModelSerializer):
    """Convierte una Categoria a JSON y valida el JSON recibido."""

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']


class ProductoSerializer(serializers.ModelSerializer):
    """Convierte un Producto a JSON y valida el JSON recibido.

    - "categoria": id de la categoría (se usa para leer y para escribir).
    - "categoria_detalle": datos completos de la categoría (solo lectura).
    """

    categoria_detalle = CategoriaSerializer(source='categoria', read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'categoria', 'categoria_detalle', 'precio', 'stock',
            'descripcion', 'estado', 'creado', 'actualizado',
        ]
        read_only_fields = ['creado', 'actualizado']

    def validate_nombre(self, valor):
        valor = valor.strip()
        if len(valor) < 3:
            raise serializers.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return valor
