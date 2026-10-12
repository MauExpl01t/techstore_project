# TechStore INACAP – Catálogo web y API REST (Django)

Sistema web interno de administración del catálogo de productos electrónicos de **TechStore INACAP**
(consolas de videojuegos, computadores, componentes y periféricos), construido con Django.

**Fase 2:** los productos se clasifican mediante una relación (`ForeignKey`) con el modelo `Categoria`,
las categorías se administran desde la interfaz web y el sistema expone una **API REST** con
Django REST Framework, protegida con **autenticación por token**.

- Proyecto: `techstore_project`
- App principal: `catalogo`
- Base de datos: MySQL 8.0 (`techstore_db`)
- Autor: MauExpl01t

📄 **Documentación del desarrollo (paso a paso, capturas y pruebas):** [docs/DOCUMENTACION.md](docs/DOCUMENTACION.md)

![Catálogo de TechStore INACAP](docs/img/04-catalogo-autenticado.png)

> La entrega de la Evaluación 2 (CRUD de productos, sin API) quedó marcada con la etiqueta de Git
> [`evaluacion-2`](https://github.com/MauExpl01t/techstore_project/tree/evaluacion-2).

---

## Credenciales de prueba (Superusuario / Admin)

| Usuario | Contraseña |
|---------|------------|
| `admin` | `admin`    |

Sirven para el login del sitio (`/login/`), el panel administrativo (`/admin/`) y para
**obtener el token de la API** (`/api/token/`).

---

## Pasos de instalación, migración y ejecución

### 1. Clonar el repositorio y entrar a la carpeta

```bash
git clone https://github.com/MauExpl01t/techstore_project.git
cd techstore_project
```

### 2. Crear y activar el entorno virtual

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Instala Django, Django REST Framework, el conector de MySQL (`mysqlclient`) y `python-dotenv`.

### 4. Crear la base de datos en MySQL

Requiere MySQL Server 8.0 o superior. El script [`mysql/crear_base_datos.sql`](mysql/crear_base_datos.sql)
crea la base `techstore_db` y el usuario `techstore_user`. Se ejecuta una sola vez como `root`:

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p -e "source mysql/crear_base_datos.sql"
```

También se puede abrir y ejecutar el script desde MySQL Workbench (**File → Open SQL Script…** y luego ⚡).

### 5. Configurar la conexión (`.env`)

Las credenciales de MySQL se leen desde un archivo `.env`, que no se sube al repositorio.
Copiar el archivo de ejemplo:

```powershell
copy .env.example .env
```

Los valores de `.env.example` ya coinciden con el usuario que crea el script del paso 4.

### 6. Aplicar migraciones

```bash
python manage.py migrate
```

Crea las tablas de Django, las del catálogo (`catalogo_categoria`, `catalogo_producto`)
y la de tokens de la API (`authtoken_token`).

### 7. Cargar datos de ejemplo y crear el superusuario

```bash
python manage.py loaddata productos
python manage.py createsuperuser
```

`loaddata` carga 5 categorías y 11 productos. Al crear el superusuario usar `admin` como nombre de
usuario y `admin` como contraseña (si Django advierte que la contraseña es poco segura, responder `y`).

### 8. Ejecutar el servidor

```bash
python manage.py runserver
```

- Sitio web: <http://127.0.0.1:8000/>
- API REST: <http://127.0.0.1:8000/api/>

### 9. (Opcional) Ejecutar las pruebas automatizadas

```bash
python manage.py test catalogo
```

Son 29 pruebas: modelos y relación, vistas web de productos y categorías, endpoints de la API y token.

---

## API REST

Base: `http://127.0.0.1:8000/api/` · Formato: JSON · Autenticación: token en la cabecera HTTP.

### Endpoints

| Método | URL | Acción | Acceso |
|--------|-----|--------|--------|
| `POST` | `/api/token/` | Obtener el token con usuario y contraseña | Público |
| `GET` | `/api/productos/` | Listar todos los productos | Público |
| `GET` | `/api/productos/<id>/` | Detalle de un producto | Público |
| `POST` | `/api/productos/` | Crear un producto | **Token** |
| `PUT` | `/api/productos/<id>/` | Edición total | **Token** |
| `PATCH` | `/api/productos/<id>/` | Edición parcial | **Token** |
| `DELETE` | `/api/productos/<id>/` | Eliminar un producto | **Token** |
| `GET` | `/api/categorias/` · `/api/categorias/<id>/` | Listar / detalle de categorías | Público |
| `POST` `PUT` `PATCH` `DELETE` | `/api/categorias/` · `/api/categorias/<id>/` | Crear, editar y eliminar categorías | **Token** |

Las peticiones privadas deben incluir la cabecera:

```
Authorization: Token <clave_del_token>
```

Sin esa cabecera, o con un token inválido, la API responde **401 Unauthorized**.

### Ejemplos con `curl`

Los ejemplos están escritos para Git Bash, Linux o macOS. Más abajo están los equivalentes para PowerShell.

**1. Listar productos (público)**

```bash
curl http://127.0.0.1:8000/api/productos/
```

**2. Detalle de un producto (público)**

```bash
curl http://127.0.0.1:8000/api/productos/2/
```

Respuesta:

```json
{
  "id": 2,
  "nombre": "Nintendo Switch OLED",
  "categoria": 1,
  "categoria_detalle": {
    "id": 1,
    "nombre": "Consolas",
    "descripcion": "Consolas de videojuegos de sobremesa y portátiles."
  },
  "precio": "379990",
  "stock": 8,
  "descripcion": "Consola híbrida Nintendo Switch modelo OLED...",
  "estado": true,
  "creado": "2026-10-04T09:00:00-03:00",
  "actualizado": "2026-10-04T09:00:00-03:00"
}
```

`categoria` es el id de la categoría (es el campo que se envía al crear o editar);
`categoria_detalle` muestra sus datos y es de solo lectura. `estado`: `true` = disponible, `false` = agotado.

**3. Intentar crear sin token (rechazado)**

```bash
curl -X POST http://127.0.0.1:8000/api/productos/ \
     -H "Content-Type: application/json" \
     -d '{"nombre": "Producto sin permiso"}'
```

```json
{"detail": "Las credenciales de autenticación no se proveyeron."}
```

Código de estado: `401`.

**4. Obtener el token**

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
     -d "username=admin&password=admin"
```

```json
{"token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"}
```

El valor es un ejemplo: cada usuario tiene su propio token. Para no copiarlo a mano en los
siguientes comandos, se puede guardar en una variable:

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/token/ -d "username=admin&password=admin" | sed 's/.*"token":"\([^"]*\)".*/\1/')
```

**5. Crear un producto (POST con token)**

```bash
curl -X POST http://127.0.0.1:8000/api/productos/ \
     -H "Authorization: Token $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"nombre": "Monitor LG UltraGear 27", "categoria": 5, "precio": 249990, "stock": 6, "descripcion": "Monitor gamer QHD 165 Hz", "estado": true}'
```

Responde `201 Created` con el producto creado, incluido su `id`.

**6. Edición total (PUT con token)** – se envían todos los campos:

```bash
curl -X PUT http://127.0.0.1:8000/api/productos/12/ \
     -H "Authorization: Token $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"nombre": "Monitor LG UltraGear 27 QHD", "categoria": 5, "precio": 239990, "stock": 4, "descripcion": "Monitor gamer QHD 165 Hz, panel IPS", "estado": true}'
```

**7. Edición parcial (PATCH con token)** – solo los campos que cambian:

```bash
curl -X PATCH http://127.0.0.1:8000/api/productos/12/ \
     -H "Authorization: Token $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"stock": 0}'
```

Responde `200 OK`. Como el stock quedó en 0, el producto pasa automáticamente a `"estado": false` (agotado).

**8. Eliminar (DELETE con token)**

```bash
curl -X DELETE http://127.0.0.1:8000/api/productos/12/ \
     -H "Authorization: Token $TOKEN"
```

Responde `204 No Content`.

> En los ejemplos 6, 7 y 8 reemplazar `12` por el `id` que devolvió el paso 5.

### Ejemplos en PowerShell (Windows)

```powershell
# Público: listar y ver detalle
Invoke-RestMethod http://127.0.0.1:8000/api/productos/
Invoke-RestMethod http://127.0.0.1:8000/api/productos/2/

# Obtener el token y armar la cabecera
$token = (Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/token/ -Body @{ username = "admin"; password = "admin" }).token
$cabecera = @{ Authorization = "Token $token" }

# Crear (POST)
$nuevo = @{ nombre = "Monitor LG UltraGear 27"; categoria = 5; precio = 249990; stock = 6; descripcion = "Monitor gamer QHD 165 Hz"; estado = $true } | ConvertTo-Json
$producto = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/productos/ -Headers $cabecera -ContentType "application/json; charset=utf-8" -Body $nuevo
$producto.id

# Edición parcial (PATCH)
Invoke-RestMethod -Method Patch -Uri "http://127.0.0.1:8000/api/productos/$($producto.id)/" -Headers $cabecera -ContentType "application/json" -Body '{"stock": 0}'

# Eliminar (DELETE)
Invoke-RestMethod -Method Delete -Uri "http://127.0.0.1:8000/api/productos/$($producto.id)/" -Headers $cabecera
```

> En Windows PowerShell 5.1 las tildes de las respuestas pueden mostrarse mal en pantalla
> (por ejemplo `PerifÃ©ricos`). Es solo la forma en que esa versión muestra el JSON: los datos
> viajan y se guardan correctamente en UTF-8. En PowerShell 7, `curl` o Postman se ven bien.

### Con Postman u otro cliente HTTP

1. `POST http://127.0.0.1:8000/api/token/` con Body → *form-data*: `username = admin`, `password = admin`. Copiar el valor de `token`.
2. En las peticiones privadas, pestaña **Headers**: clave `Authorization`, valor `Token <clave_del_token>`
   (la palabra `Token`, un espacio y la clave).
3. Para POST, PUT y PATCH: Body → *raw* → **JSON**.

### Códigos de respuesta

| Código | Significado |
|--------|-------------|
| `200 OK` | Lectura o edición correcta |
| `201 Created` | Producto creado |
| `204 No Content` | Producto eliminado |
| `400 Bad Request` | Datos inválidos (por ejemplo precio negativo o categoría inexistente); el JSON indica el campo con error |
| `401 Unauthorized` | Falta el token o no es válido |
| `404 Not Found` | No existe un producto con ese id |
| `409 Conflict` | Se intentó eliminar una categoría que todavía tiene productos |

---

## Rutas del sitio web

| URL | Vista | Acceso |
|-----|-------|--------|
| `/` | Catálogo (tarjetas), con búsqueda y filtro por categoría | Público |
| `/producto/<id>/` | Detalle técnico | Público |
| `/producto/nuevo/` | Crear producto | Privado (`@login_required`) |
| `/producto/<id>/editar/` | Modificar producto | Privado (`@login_required`) |
| `/producto/<id>/eliminar/` | Confirmar eliminación | Privado (`@login_required`) |
| `/categorias/` | Listado de categorías | Público |
| `/categorias/nueva/` | Crear categoría | Privado (`@login_required`) |
| `/categorias/<id>/editar/` | Modificar categoría | Privado (`@login_required`) |
| `/login/` · `/logout/` | Login / Logout (`django.contrib.auth`) | — |
| `/admin/` | Panel administrativo de Django | Staff |

Si un usuario anónimo intenta entrar a una vista privada, es redirigido a `/login/?next=...`
y, tras iniciar sesión, vuelve a la página que pidió.

---

## Estructura del proyecto

```
techstore_project/   (raíz del repositorio)
├── manage.py
├── requirements.txt            # Django, Django REST Framework, mysqlclient, python-dotenv
├── README.md
├── .env.example                # Modelo de credenciales de MySQL
├── mysql/
│   └── crear_base_datos.sql    # Crea la base de datos y el usuario
├── docs/
│   ├── DOCUMENTACION.md        # Documentación del desarrollo
│   └── img/                    # Capturas de pantalla
├── techstore_project/          # Configuración del proyecto
│   ├── settings.py             # Apps, base de datos, REST_FRAMEWORK
│   └── urls.py                 # admin, login, logout, api/ e include de catalogo
└── catalogo/                   # App principal
    ├── models.py               # Modelos Categoria y Producto (ForeignKey)
    ├── forms.py                # CategoriaForm, ProductoForm (ModelForm) y LoginForm
    ├── views.py                # Vistas web de productos y categorías
    ├── urls.py                 # Rutas web
    ├── serializers.py          # CategoriaSerializer y ProductoSerializer (API)
    ├── api_views.py            # ProductoViewSet y CategoriaViewSet (API)
    ├── api_urls.py             # Rutas de la API y endpoint del token
    ├── admin.py                # Registro en el panel administrativo
    ├── tests.py                # 29 pruebas automatizadas
    ├── migrations/
    │   ├── 0001_initial.py
    │   └── 0002_categoria_y_relacion.py   # Crea Categoria y convierte el texto en ForeignKey
    ├── fixtures/productos.json # Categorías y productos de ejemplo
    ├── templatetags/formato.py # Filtro |clp para precios ($549.990)
    ├── static/catalogo/css/estilos.css
    └── templates/
        ├── base.html           # Layout principal con navbar dinámica
        ├── registration/login.html
        └── catalogo/
            ├── lista.html
            ├── detalle.html
            ├── categorias.html         # Listado de categorías
            ├── formulario.html         # Crear y editar (productos y categorías)
            └── confirmar_eliminar.html
```

---

## Cumplimiento de la pauta – Evaluación 3 (Fase 2)

### 1. Modelos y relaciones (15 pts) – `catalogo/models.py`

- **`Categoria`**: `nombre` (`CharField`, único) y `descripcion` (`TextField`, opcional con `blank=True`).
- **`Producto`**: el campo de texto `categoria` se reemplazó por
  `ForeignKey(Categoria, on_delete=PROTECT, related_name='productos')`. Se mantienen `nombre`, `precio`,
  `stock`, `descripcion` y `estado` (disponible/agotado).
- `on_delete=PROTECT` impide borrar una categoría que todavía tiene productos.
- **Migración** `0002_categoria_y_relacion.py`: crea la tabla de categorías, convierte los datos existentes
  (cada producto queda enlazado a su categoría) y elimina el campo de texto, sin pérdida de datos.

### 2. Vistas y formularios web (25 pts) – `catalogo/views.py`, `catalogo/forms.py`

- **Gestión de categorías**: `lista_categorias` (pública), `crear_categoria` y `editar_categoria`,
  con el `ModelForm` `CategoriaForm` y la plantilla `categorias.html`.
- **Formulario de productos**: en `ProductoForm` el campo `categoria` es un `Select` cuyas opciones se
  consultan a la tabla de categorías en cada carga; una categoría nueva aparece en el desplegable de inmediato.
- **Seguridad**: `@login_required` en crear y editar categorías, y en crear, editar y eliminar productos.

### 3. API REST (30 pts) – `catalogo/serializers.py`, `catalogo/api_views.py`, `catalogo/api_urls.py`

- **Serializadores**: `CategoriaSerializer` y `ProductoSerializer` (`ModelSerializer` de DRF).
- **Endpoints**: `ProductoViewSet` (`ModelViewSet`) registrado en un `DefaultRouter` expone listar, detallar,
  crear, modificar (PUT y PATCH) y eliminar en `/api/productos/` y `/api/productos/<id>/`, en formato JSON.

### 4. Seguridad y autenticación por token (20 pts) – `techstore_project/settings.py`

- `rest_framework.authtoken` en `INSTALLED_APPS` y endpoint `/api/token/` con `obtain_auth_token`.
- `TokenAuthentication` + permiso `IsAuthenticatedOrReadOnly`: GET es público; POST, PUT, PATCH y DELETE
  exigen la cabecera `Authorization: Token <clave>` y, sin ella, responden 401.

### 5. Entregables y documentación (10 pts)

- Proyecto `techstore_project` con la app `catalogo`, versionado en Git.
- `requirements.txt` con Django, Django REST Framework y las demás librerías.
- Este `README.md` con instalación, credenciales y ejemplos de consumo de la API con token.

---

## Tecnologías

- Python 3 / Django 5.2 LTS / Django REST Framework 3.18 (ver `requirements.txt`)
- MySQL 8.0 (conector `mysqlclient`)
- Bootstrap 5 y Bootstrap Icons (CDN)
