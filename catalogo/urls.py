from django.urls import path

from . import views

app_name = 'catalogo'

urlpatterns = [
    # Productos
    path('', views.lista_productos, name='lista'),
    path('producto/<int:pk>/', views.detalle_producto, name='detalle'),
    path('producto/nuevo/', views.crear_producto, name='crear'),
    path('producto/<int:pk>/editar/', views.editar_producto, name='editar'),
    path('producto/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar'),
    # Categorías
    path('categorias/', views.lista_categorias, name='categorias'),
    path('categorias/nueva/', views.crear_categoria, name='crear_categoria'),
    path('categorias/<int:pk>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:pk>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),
]
