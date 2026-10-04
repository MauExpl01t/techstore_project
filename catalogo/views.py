from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductoForm
from .models import Producto


# ---------- Vistas públicas ----------

def lista_productos(request):
    """Catálogo principal en tarjetas, con búsqueda y filtro por categoría."""
    productos = Producto.objects.all()

    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '')

    if q:
        productos = productos.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    if categoria in Producto.Categoria.values:
        productos = productos.filter(categoria=categoria)

    return render(request, 'catalogo/lista.html', {
        'productos': productos,
        'categorias': Producto.Categoria.choices,
        'categoria_actual': categoria,
        'q': q,
    })


def detalle_producto(request, pk):
    """Ficha técnica de un producto."""
    producto = get_object_or_404(Producto, pk=pk)
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
        'producto': producto,
        'titulo': f'Editar: {producto.nombre}',
        'boton': 'Guardar cambios',
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
