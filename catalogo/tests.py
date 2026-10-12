from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Categoria, Producto


class ModelosTests(TestCase):
    def setUp(self):
        self.consolas = Categoria.objects.create(nombre='Consolas')

    def test_stock_cero_queda_agotado(self):
        producto = Producto.objects.create(
            nombre='Xbox Series S', categoria=self.consolas,
            precio=329990, stock=0, descripcion='Consola digital', estado=True,
        )
        self.assertFalse(producto.estado)

    def test_relacion_categoria_productos(self):
        producto = Producto.objects.create(
            nombre='PlayStation 5', categoria=self.consolas,
            precio=549990, stock=10, descripcion='Consola Sony',
        )
        # Desde el producto se llega a la categoría y desde la categoría a sus productos
        self.assertEqual(producto.categoria.nombre, 'Consolas')
        self.assertIn(producto, self.consolas.productos.all())


class VistasProductoTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('tester', password='clave-segura-123')
        self.consolas = Categoria.objects.create(nombre='Consolas')
        self.notebooks = Categoria.objects.create(nombre='Notebooks')
        self.producto = Producto.objects.create(
            nombre='PlayStation 5', categoria=self.consolas,
            precio=549990, stock=10, descripcion='Consola Sony',
        )
        self.datos = {
            'nombre': 'Notebook HP Victus', 'categoria': self.notebooks.pk,
            'precio': 799990, 'stock': 3, 'descripcion': 'Ryzen 5, RTX 3050', 'estado': 'True',
        }

    # --- Vistas públicas ---
    def test_lista_publica(self):
        respuesta = self.client.get(reverse('catalogo:lista'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'PlayStation 5')
        self.assertContains(respuesta, 'Iniciar sesión')

    def test_filtro_por_categoria(self):
        respuesta = self.client.get(reverse('catalogo:lista'), {'categoria': self.notebooks.pk})
        self.assertNotContains(respuesta, 'PlayStation 5')

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
    def test_formulario_muestra_categorias_de_la_base(self):
        self.client.force_login(self.usuario)
        Categoria.objects.create(nombre='Monitores')
        respuesta = self.client.get(reverse('catalogo:crear'))
        self.assertContains(respuesta, '<option value="%d">Monitores</option>' % Categoria.objects.get(nombre='Monitores').pk)

    def test_crear_producto(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.post(reverse('catalogo:crear'), self.datos)
        nuevo = Producto.objects.get(nombre='Notebook HP Victus')
        self.assertRedirects(respuesta, nuevo.get_absolute_url())
        self.assertEqual(nuevo.categoria, self.notebooks)

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


class VistasCategoriaTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('tester', password='clave-segura-123')
        self.categoria = Categoria.objects.create(nombre='Consolas', descripcion='Videojuegos')

    def test_lista_publica(self):
        respuesta = self.client.get(reverse('catalogo:categorias'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Consolas')

    def test_crear_y_editar_requieren_login(self):
        urls = [
            reverse('catalogo:crear_categoria'),
            reverse('catalogo:editar_categoria', args=[self.categoria.pk]),
        ]
        for url in urls:
            respuesta = self.client.get(url)
            self.assertRedirects(respuesta, f"{reverse('login')}?next={url}")

    def test_crear_categoria(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.post(reverse('catalogo:crear_categoria'), {'nombre': 'Monitores', 'descripcion': ''})
        self.assertRedirects(respuesta, reverse('catalogo:categorias'))
        self.assertTrue(Categoria.objects.filter(nombre='Monitores').exists())

    def test_editar_categoria(self):
        self.client.force_login(self.usuario)
        self.client.post(
            reverse('catalogo:editar_categoria', args=[self.categoria.pk]),
            {'nombre': 'Consolas y juegos', 'descripcion': 'Videojuegos'},
        )
        self.categoria.refresh_from_db()
        self.assertEqual(self.categoria.nombre, 'Consolas y juegos')

    def test_nombre_duplicado_no_se_guarda(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.post(reverse('catalogo:crear_categoria'), {'nombre': 'Consolas'})
        self.assertContains(respuesta, 'Ya existe una categoría con ese nombre.')
        self.assertEqual(Categoria.objects.count(), 1)


class ApiProductosTests(APITestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('tester', password='clave-segura-123')
        self.consolas = Categoria.objects.create(nombre='Consolas')
        self.producto = Producto.objects.create(
            nombre='PlayStation 5', categoria=self.consolas,
            precio=549990, stock=10, descripcion='Consola Sony',
        )
        self.url_lista = '/api/productos/'
        self.url_detalle = f'/api/productos/{self.producto.pk}/'
        self.datos = {
            'nombre': 'Nintendo Switch OLED', 'categoria': self.consolas.pk,
            'precio': 379990, 'stock': 8, 'descripcion': 'Consola híbrida', 'estado': True,
        }

    def autenticar(self):
        token = Token.objects.create(user=self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    # --- Endpoints públicos (lectura) ---
    def test_listar_es_publico(self):
        respuesta = self.client.get(self.url_lista)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.json()), 1)

    def test_detalle_es_publico(self):
        respuesta = self.client.get(self.url_detalle)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        datos = respuesta.json()
        self.assertEqual(datos['nombre'], 'PlayStation 5')
        self.assertEqual(datos['categoria'], self.consolas.pk)
        self.assertEqual(datos['categoria_detalle']['nombre'], 'Consolas')

    # --- Endpoints privados sin token: 401 ---
    def test_escritura_sin_token_es_rechazada(self):
        self.assertEqual(self.client.post(self.url_lista, self.datos, format='json').status_code,
                         status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.put(self.url_detalle, self.datos, format='json').status_code,
                         status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.patch(self.url_detalle, {'stock': 1}, format='json').status_code,
                         status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.delete(self.url_detalle).status_code,
                         status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Producto.objects.count(), 1)

    def test_token_invalido_es_rechazado(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token clave-que-no-existe')
        respuesta = self.client.post(self.url_lista, self.datos, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Endpoints privados con token ---
    def test_crear_con_token(self):
        self.autenticar()
        respuesta = self.client.post(self.url_lista, self.datos, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Producto.objects.filter(nombre='Nintendo Switch OLED').exists())

    def test_put_con_token(self):
        self.autenticar()
        respuesta = self.client.put(self.url_detalle, self.datos, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nombre, 'Nintendo Switch OLED')

    def test_patch_con_token(self):
        self.autenticar()
        respuesta = self.client.patch(self.url_detalle, {'stock': 0}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 0)
        self.assertFalse(self.producto.estado)   # regla de negocio: stock 0 = agotado

    def test_delete_con_token(self):
        self.autenticar()
        respuesta = self.client.delete(self.url_detalle)
        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Producto.objects.filter(pk=self.producto.pk).exists())

    def test_datos_invalidos_devuelven_400(self):
        self.autenticar()
        self.datos['precio'] = -5
        respuesta = self.client.post(self.url_lista, self.datos, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('precio', respuesta.json())


class ApiTokenTests(APITestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('tester', password='clave-segura-123')

    def test_obtener_token_con_credenciales_correctas(self):
        respuesta = self.client.post('/api/token/', {'username': 'tester', 'password': 'clave-segura-123'})
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json()['token'], Token.objects.get(user=self.usuario).key)

    def test_credenciales_incorrectas_no_entregan_token(self):
        respuesta = self.client.post('/api/token/', {'username': 'tester', 'password': 'mala'})
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)


class ApiCategoriasTests(APITestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('tester', password='clave-segura-123')
        self.consolas = Categoria.objects.create(nombre='Consolas')
        Producto.objects.create(
            nombre='PlayStation 5', categoria=self.consolas,
            precio=549990, stock=10, descripcion='Consola Sony',
        )

    def test_listar_es_publico(self):
        respuesta = self.client.get('/api/categorias/')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_no_se_elimina_categoria_con_productos(self):
        token = Token.objects.create(user=self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        respuesta = self.client.delete(f'/api/categorias/{self.consolas.pk}/')
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(Categoria.objects.filter(pk=self.consolas.pk).exists())
