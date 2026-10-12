from django.contrib import admin

from .models import Categoria, Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock', 'estado', 'actualizado')
    list_filter = ('categoria', 'estado')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('precio', 'stock')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)
