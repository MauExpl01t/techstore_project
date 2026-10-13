from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.files.uploadedfile import UploadedFile

from .models import Categoria, Producto


class MarcarErroresMixin:
    """Agrega la clase Bootstrap is-invalid a los campos con errores."""

    def _post_clean(self):
        super()._post_clean()
        for nombre_campo in self.errors:
            if nombre_campo in self.fields:
                widget = self.fields[nombre_campo].widget
                widget.attrs['class'] = f"{widget.attrs.get('class', '')} is-invalid".strip()


class CategoriaForm(MarcarErroresMixin, forms.ModelForm):
    """Formulario de creación/edición de categorías."""

    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Monitores',
                'autofocus': True,
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Qué tipo de productos agrupa esta categoría (opcional)',
            }),
        }
        error_messages = {
            'nombre': {'unique': 'Ya existe una categoría con ese nombre.'},
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre


class ProductoForm(MarcarErroresMixin, forms.ModelForm):
    """Formulario de creación/edición de productos con widgets personalizados."""

    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'precio', 'stock', 'descripcion', 'imagen', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: PlayStation 5 Slim 1TB',
                'autofocus': True,
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select',
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 549990',
                'min': 0,
                'step': 1,
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unidades en bodega',
                'min': 0,
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Especificaciones técnicas: procesador, memoria, almacenamiento, conectividad...',
            }),
            'estado': forms.RadioSelect(attrs={
                'class': 'form-check-input',
            }),
        }
        help_texts = {
            'precio': 'Valor en pesos chilenos, sin puntos ni decimales.',
            'stock': 'Si el stock es 0 el producto quedará como agotado.',
            'imagen': 'Opcional. Foto del producto en JPG o PNG, de hasta 2 MB.',
        }

    TAMANO_MAXIMO_IMAGEN = 2 * 1024 * 1024  # 2 MB

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Como "categoria" es una ForeignKey, Django crea un ModelChoiceField:
        # las opciones del <select> se consultan a la tabla de categorías en cada carga.
        self.fields['categoria'].queryset = Categoria.objects.order_by('nombre')
        self.fields['categoria'].empty_label = 'Selecciona una categoría'

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre

    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        # Solo se revisa el tamaño cuando se sube un archivo nuevo
        if isinstance(imagen, UploadedFile) and imagen.size > self.TAMANO_MAXIMO_IMAGEN:
            raise forms.ValidationError('La imagen no puede pesar más de 2 MB.')
        return imagen


class LoginForm(AuthenticationForm):
    """Formulario de login de django.contrib.auth con clases CSS."""

    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'autofocus': True,
        }),
    )
    password = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password',
        }),
    )
