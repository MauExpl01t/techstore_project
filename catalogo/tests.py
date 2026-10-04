from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Producto


class ProductoModelTests(TestCase):
    def test_stock_cero_queda_agotado(self):
        producto = Producto.objects.create(
            nombre='Xbox Series S', categoria=Producto.Categoria.CONSOLAS,
            precio=329990, stock=0, descripcion='Consola digital', estado=True,
        )
        self.assertFalse(producto.estado)


class VistasTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('tester', password='clave-segura-123')
        self.producto = Producto.objects.create(
            nombre='PlayStation 5', categoria=Producto.Categoria.CONSOLAS,
            precio=549990, stock=10, descripcion='Consola Sony',
        )
        self.datos = {
            'nombre': 'Notebook HP Victus', 'categoria': Producto.Categoria.NOTEBOOKS,
            'precio': 799990, 'stock': 3, 'descripcion': 'Ryzen 5, RTX 3050', 'estado': 'True',
        }

    # --- Vistas públicas ---
    def test_lista_publica(self):
        respuesta = self.client.get(reverse('catalogo:lista'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'PlayStation 5')
        self.assertContains(respuesta, 'Iniciar sesión')

    def test_detalle_publico(self):
        respuesta = self.client.get(reverse('catalogo:detalle', args=[self.producto.pk]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Ficha técnica')

    # --- Vistas privadas sin sesión: redirigen al login ---
    def test_vistas_privadas_requieren_login(self):
        urls = [
            reverse('catalogo:crear'),
            reverse('catalogo:editar', args=[self.producto.pk]),
            reverse('catalogo:eliminar', args=[self.producto.pk]),
        ]
        for url in urls:
            respuesta = self.client.get(url)
            self.assertRedirects(respuesta, f"{reverse('login')}?next={url}")

    # --- CRUD con sesión iniciada ---
    def test_crear_producto(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.post(reverse('catalogo:crear'), self.datos)
        nuevo = Producto.objects.get(nombre='Notebook HP Victus')
        self.assertRedirects(respuesta, nuevo.get_absolute_url())

    def test_editar_producto(self):
        self.client.force_login(self.usuario)
        self.datos['nombre'] = 'PlayStation 5 Pro'
        self.client.post(reverse('catalogo:editar', args=[self.producto.pk]), self.datos)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nombre, 'PlayStation 5 Pro')

    def test_eliminar_producto(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(reverse('catalogo:eliminar', args=[self.producto.pk]))
        self.assertContains(respuesta, 'Confirmar eliminación')
        self.client.post(reverse('catalogo:eliminar', args=[self.producto.pk]))
        self.assertFalse(Producto.objects.filter(pk=self.producto.pk).exists())

    def test_navbar_usuario_autenticado(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(reverse('catalogo:lista'))
        self.assertContains(respuesta, 'Cerrar sesión')
        self.assertContains(respuesta, 'Nuevo producto')
