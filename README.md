# TechStore INACAP – CRUD de Productos (Django)

Sistema web interno de administración del catálogo de productos electrónicos de **TechStore INACAP**
(consolas de videojuegos, computadores, componentes y periféricos), construido con Django.

- Proyecto: `techstore_project`
- App principal: `catalogo`
- Base de datos: SQLite (`db.sqlite3`)

---

## Credenciales de prueba (Superusuario / Admin)

| Usuario | Contraseña      |
|---------|-----------------|
| `admin` | `TechStore2026` |

Sirven tanto para el login del sitio (`/login/`) como para el panel administrativo (`/admin/`).

---

## Pasos de ejecución

### 1. Clonar el repositorio y entrar a la carpeta

```bash
git clone <url-del-repositorio>
cd BACK_END_2
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

### 4. Aplicar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Cargar productos de ejemplo y crear el superusuario

> El repositorio ya incluye `db.sqlite3` con los productos de ejemplo y el usuario `admin`.
> Este paso solo es necesario si se parte con una base de datos vacía.

```bash
python manage.py loaddata productos
python manage.py createsuperuser
```

Al crear el superusuario usar `admin` como nombre de usuario y `TechStore2026` como contraseña
(si Django advierte que la contraseña es poco segura, responder `y`).

### 6. Ejecutar el servidor

```bash
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/>.

### 7. (Opcional) Ejecutar las pruebas automatizadas

```bash
python manage.py test catalogo
```

---

## Rutas del sistema

| URL                          | Vista               | Acceso                |
|------------------------------|---------------------|-----------------------|
| `/`                          | Catálogo (tarjetas) | Público               |
| `/producto/<id>/`            | Detalle técnico     | Público               |
| `/producto/nuevo/`           | Crear producto      | Privado (`@login_required`) |
| `/producto/<id>/editar/`     | Modificar producto  | Privado (`@login_required`) |
| `/producto/<id>/eliminar/`   | Confirmar eliminación | Privado (`@login_required`) |
| `/login/` · `/logout/`       | Login / Logout (`django.contrib.auth`) | — |
| `/admin/`                    | Panel administrativo de Django | Staff |

Si un usuario anónimo intenta entrar a una vista privada, es redirigido a `/login/?next=...`
y, tras iniciar sesión, vuelve a la página que pidió.

---

## Estructura del proyecto

```
BACK_END_2/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3
├── techstore_project/          # Configuración del proyecto
│   ├── settings.py
│   └── urls.py                 # admin, login, logout e include de catalogo
└── catalogo/                   # App principal
    ├── models.py               # Modelo Producto
    ├── forms.py                # ProductoForm (ModelForm + widgets) y LoginForm
    ├── views.py                # CRUD (vistas públicas y privadas)
    ├── urls.py
    ├── admin.py                # Registro en el panel administrativo
    ├── tests.py                # Pruebas automatizadas
    ├── migrations/
    ├── fixtures/productos.json # Datos de ejemplo
    ├── templatetags/formato.py # Filtro |clp para precios ($549.990)
    ├── static/catalogo/css/estilos.css
    └── templates/
        ├── base.html           # Layout principal con navbar dinámica
        ├── registration/login.html
        └── catalogo/
            ├── lista.html
            ├── detalle.html
            ├── formulario.html         # Crear y editar
            └── confirmar_eliminar.html
```

---

## Cumplimiento de la pauta de evaluación

### 1. Modelos de datos (15 pts) – `catalogo/models.py`
Modelo `Producto` con los campos solicitados y tipos idóneos:

| Campo         | Tipo                | Detalle |
|---------------|---------------------|---------|
| `nombre`      | `CharField`         | máx. 120 caracteres |
| `categoria`   | `CharField` + choices | Consolas, Notebooks, Computadores de escritorio, Componentes, Periféricos |
| `precio`      | `DecimalField`      | pesos chilenos, sin decimales, ≥ 0 |
| `stock`       | `IntegerField`      | ≥ 0 |
| `descripcion` | `TextField`         | ficha técnica |
| `estado`      | `BooleanField`      | `True` = Disponible / `False` = Agotado |
| `creado`, `actualizado` | `DateTimeField` | automáticos |

Regla de negocio: si el stock es 0, al guardar el producto queda automáticamente como **agotado**.
La migración inicial está en `catalogo/migrations/0001_initial.py`.

### 2. Conexión a BD (10 pts)
SQLite configurado en `settings.DATABASES`. Todos los datos se leen y escriben con el ORM
(`Producto.objects.all()`, `filter()`, `get_object_or_404`, `form.save()`, `delete()`),
y el modelo está registrado en el panel `/admin/` con filtros, búsqueda y edición rápida.

### 3. Vistas y lógica CRUD (25 pts) – `catalogo/views.py`
- **Listar**: `lista_productos` (con búsqueda por texto y filtro por categoría).
- **Ver detalle**: `detalle_producto`.
- **Crear**: `crear_producto` – `@login_required`.
- **Editar**: `editar_producto` – `@login_required`.
- **Eliminar**: `eliminar_producto` – `@login_required`; con GET muestra la confirmación y solo elimina con POST.
- Login y logout con `LoginView` y `LogoutView` de `django.contrib.auth` (`techstore_project/urls.py`).

### 4. Templates y navegación (25 pts)
- `base.html` es el layout principal; todas las páginas usan `{% extends 'base.html' %}`.
- La barra de navegación cambia según `user.is_authenticated`:
  - **Anónimo**: muestra "Visitante" y el botón *Iniciar sesión*.
  - **Autenticado**: muestra *Nuevo producto*, *Panel admin* (si es staff), el saludo con el nombre del usuario y *Cerrar sesión*.
- El catálogo presenta los productos en **tarjetas (cards)** en grilla, con ícono y color según la categoría (consolas, notebooks, PC de escritorio, etc.), badge de estado y precio.

### 5. Formularios y widgets (25 pts) – `catalogo/forms.py`
`ProductoForm` es un `ModelForm` con widgets personalizados:
- `TextInput`, `NumberInput` y `Textarea` con clase `form-control` y placeholders.
- `Select` (lista desplegable de categorías) con clase `form-select`.
- `RadioSelect` (selección Disponible/Agotado) con clase `form-check-input`.
- Los campos con error se marcan en rojo (`is-invalid`) y los mensajes se muestran bajo cada campo.

El formulario de login (`LoginForm`) también usa widgets con clases CSS.

---

## Tecnologías

- Python 3 / Django (ver `requirements.txt`)
- Bootstrap 5 y Bootstrap Icons (CDN)
- SQLite
