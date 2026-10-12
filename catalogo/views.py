from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CategoriaForm, ProductoForm
from .models import Categoria, Producto


# ==================== PRODUCTOS ====================

# ---------- Vistas públicas ----------

def lista_productos(request):
    """Catálogo principal en tarjetas, con búsqueda y filtro por categoría."""
    # select_related trae la categoría de cada producto en la misma consulta (JOIN)
    productos = Producto.objects.select_related('categoria')

    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '')

    if q:
        productos = productos.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    if categoria.isdigit():
        productos = productos.filter(categoria_id=categoria)

    return render(request, 'catalogo/lista.html', {
        'productos': productos,
        'categorias': Categoria.objects.all(),
        'categoria_actual': categoria,
        'q': q,
    })


def detalle_producto(request, pk):
    """Ficha técnica de un producto."""
    producto = get_object_or_404(Producto.objects.select_related('categoria'), pk=pk)
    return render(request, 'catalogo/detalle.html', {'producto': producto})


# ---------- Vistas privadas (requieren inicio de sesión) ----------

@login_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre}" creado correctamente.')
            return redirect(producto)
    else:
        form = ProductoForm()

    return render(request, 'catalogo/formulario.html', {
        'form': form,
        'titulo': 'Nuevo producto',
        'boton': 'Crear producto',
        'cancelar_url': reverse('catalogo:lista'),
    })


@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado correctamente.')
            return redirect(producto)
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'catalogo/formulario.html', {
        'form': form,
        'titulo': f'Editar: {producto.nombre}',
        'boton': 'Guardar cambios',
        'cancelar_url': producto.get_absolute_url(),
    })


@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre}" eliminado.')
        return redirect('catalogo:lista')

    return render(request, 'catalogo/confirmar_eliminar.html', {'producto': producto})


# ==================== CATEGORÍAS ====================

def lista_categorias(request):
    """Listado público de categorías con la cantidad de productos de cada una."""
    categorias = Categoria.objects.annotate(total_productos=Count('productos')).order_by('nombre')
    return render(request, 'catalogo/categorias.html', {'categorias': categorias})


@login_required
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" creada correctamente.')
            return redirect('catalogo:categorias')
    else:
        form = CategoriaForm()

    return render(request, 'catalogo/formulario.html', {
        'form': form,
        'titulo': 'Nueva categoría',
        'boton': 'Crear categoría',
        'cancelar_url': reverse('catalogo:categorias'),
    })


@login_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" actualizada correctamente.')
            return redirect('catalogo:categorias')
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, 'catalogo/formulario.html', {
        'form': form,
        'titulo': f'Editar categoría: {categoria.nombre}',
        'boton': 'Guardar cambios',
        'cancelar_url': reverse('catalogo:categorias'),
    })
