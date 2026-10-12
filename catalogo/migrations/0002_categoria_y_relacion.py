import django.db.models.deletion
from django.db import migrations, models

# Valores que tenía el campo de texto "categoria" y la categoría que les corresponde
CATEGORIAS_ANTERIORES = [
    ('CONSOLAS', 'Consolas', 'Consolas de videojuegos de sobremesa y portátiles.'),
    ('NOTEBOOKS', 'Notebooks', 'Computadores portátiles para estudio, trabajo y juegos.'),
    ('ESCRITORIO', 'Computadores de escritorio', 'Equipos de escritorio armados y de marca.'),
    ('COMPONENTES', 'Componentes', 'Piezas internas: tarjetas de video, almacenamiento, memorias y procesadores.'),
    ('PERIFERICOS', 'Periféricos', 'Teclados, mouses y otros accesorios externos.'),
]


def texto_a_relacion(apps, schema_editor):
    """Crea las categorías que estaban en uso y enlaza cada producto con la suya."""
    Categoria = apps.get_model('catalogo', 'Categoria')
    Producto = apps.get_model('catalogo', 'Producto')

    en_uso = set(Producto.objects.order_by().values_list('categoria_texto', flat=True).distinct())
    for codigo, nombre, descripcion in CATEGORIAS_ANTERIORES:
        if codigo in en_uso:
            categoria = Categoria.objects.create(nombre=nombre, descripcion=descripcion)
            Producto.objects.filter(categoria_texto=codigo).update(categoria=categoria)

    # Valores que no estaban en la lista original (por si se cargaron a mano)
    for codigo in en_uso - {c[0] for c in CATEGORIAS_ANTERIORES}:
        categoria = Categoria.objects.create(nombre=codigo.capitalize())
        Producto.objects.filter(categoria_texto=codigo).update(categoria=categoria)


def relacion_a_texto(apps, schema_editor):
    """Operación inversa: vuelve a escribir el código de texto en cada producto."""
    Producto = apps.get_model('catalogo', 'Producto')
    codigos = {nombre: codigo for codigo, nombre, _ in CATEGORIAS_ANTERIORES}
    for producto in Producto.objects.order_by().select_related('categoria'):
        nombre = producto.categoria.nombre
        producto.categoria_texto = codigos.get(nombre, nombre.upper()[:20])
        producto.save(update_fields=['categoria_texto'])


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0001_initial'),
    ]

    operations = [
        # 1. Nueva tabla de categorías
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=80, unique=True, verbose_name='nombre')),
                ('descripcion', models.TextField(blank=True, verbose_name='descripción')),
            ],
            options={
                'verbose_name': 'categoría',
                'verbose_name_plural': 'categorías',
                'ordering': ['nombre'],
            },
        ),
        # 2. El campo de texto se conserva temporalmente con otro nombre
        migrations.AlterModelOptions(
            name='producto',
            options={'ordering': ['nombre'], 'verbose_name': 'producto', 'verbose_name_plural': 'productos'},
        ),
        migrations.RenameField(
            model_name='producto',
            old_name='categoria',
            new_name='categoria_texto',
        ),
        # 3. Clave foránea, vacía por ahora
        migrations.AddField(
            model_name='producto',
            name='categoria',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='productos',
                to='catalogo.categoria',
                verbose_name='categoría',
            ),
        ),
        # 4. Se traspasan los datos del texto a la relación
        migrations.RunPython(texto_a_relacion, relacion_a_texto),
        # 5. Se elimina el campo de texto y la relación pasa a ser obligatoria
        migrations.RemoveField(
            model_name='producto',
            name='categoria_texto',
        ),
        migrations.AlterField(
            model_name='producto',
            name='categoria',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='productos',
                to='catalogo.categoria',
                verbose_name='categoría',
            ),
        ),
        migrations.AlterModelOptions(
            name='producto',
            options={
                'ordering': ['categoria__nombre', 'nombre'],
                'verbose_name': 'producto',
                'verbose_name_plural': 'productos',
            },
        ),
    ]
