from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Categoria(models.Model):
    """Categoría que clasifica los productos del catálogo."""

    nombre = models.CharField('nombre', max_length=80, unique=True)
    descripcion = models.TextField('descripción', blank=True)

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """Producto electrónico del catálogo de TechStore INACAP."""

    # estado: True = disponible, False = agotado
    ESTADO_CHOICES = [
        (True, 'Disponible'),
        (False, 'Agotado'),
    ]

    # Ícono (Bootstrap Icons) usado en las tarjetas según el nombre de la categoría
    ICONOS = {
        'consolas': 'bi-controller',
        'notebooks': 'bi-laptop',
        'computadores de escritorio': 'bi-pc-display',
        'componentes': 'bi-cpu',
        'periféricos': 'bi-keyboard',
    }

    nombre = models.CharField('nombre', max_length=120)
    # Relación muchos a uno: muchos productos pertenecen a una categoría.
    # PROTECT impide borrar una categoría que todavía tiene productos.
    categoria = models.ForeignKey(
        Categoria,
        verbose_name='categoría',
        on_delete=models.PROTECT,
        related_name='productos',
    )
    precio = models.DecimalField(
        'precio (CLP)',
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(0)],
    )
    stock = models.IntegerField(
        'stock',
        default=0,
        validators=[MinValueValidator(0)],
    )
    descripcion = models.TextField('descripción técnica')
    # Foto del producto (opcional). El archivo se guarda en media/productos/
    # y en la base de datos solo queda su ruta.
    imagen = models.ImageField('imagen', upload_to='productos/', blank=True)
    estado = models.BooleanField('estado', choices=ESTADO_CHOICES, default=True)
    creado = models.DateTimeField('creado', auto_now_add=True)
    actualizado = models.DateTimeField('actualizado', auto_now=True)

    class Meta:
        verbose_name = 'producto'
        verbose_name_plural = 'productos'
        ordering = ['categoria__nombre', 'nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        # Un producto sin stock no puede figurar como disponible
        if self.stock == 0:
            self.estado = False
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalogo:detalle', args=[self.pk])

    @property
    def icono(self):
        return self.ICONOS.get(self.categoria.nombre.lower(), 'bi-box-seam')
