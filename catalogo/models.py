from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Producto(models.Model):
    """Producto electrónico del catálogo de TechStore INACAP."""

    class Categoria(models.TextChoices):
        CONSOLAS = 'CONSOLAS', 'Consolas'
        NOTEBOOKS = 'NOTEBOOKS', 'Notebooks'
        ESCRITORIO = 'ESCRITORIO', 'Computadores de escritorio'
        COMPONENTES = 'COMPONENTES', 'Componentes'
        PERIFERICOS = 'PERIFERICOS', 'Periféricos'

    # estado: True = disponible, False = agotado
    ESTADO_CHOICES = [
        (True, 'Disponible'),
        (False, 'Agotado'),
    ]

    # Ícono (Bootstrap Icons) usado en las tarjetas según la categoría
    ICONOS = {
        Categoria.CONSOLAS: 'bi-controller',
        Categoria.NOTEBOOKS: 'bi-laptop',
        Categoria.ESCRITORIO: 'bi-pc-display',
        Categoria.COMPONENTES: 'bi-cpu',
        Categoria.PERIFERICOS: 'bi-keyboard',
    }

    nombre = models.CharField('nombre', max_length=120)
    categoria = models.CharField(
        'categoría',
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.CONSOLAS,
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
    estado = models.BooleanField('estado', choices=ESTADO_CHOICES, default=True)
    creado = models.DateTimeField('creado', auto_now_add=True)
    actualizado = models.DateTimeField('actualizado', auto_now=True)

    class Meta:
        verbose_name = 'producto'
        verbose_name_plural = 'productos'
        ordering = ['categoria', 'nombre']

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
        return self.ICONOS.get(self.categoria, 'bi-box-seam')
