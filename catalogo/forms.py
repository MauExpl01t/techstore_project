from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Producto


class ProductoForm(forms.ModelForm):
    """Formulario de creación/edición de productos con widgets personalizados."""

    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'precio', 'stock', 'descripcion', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: PlayStation 5 Slim 1TB',
                'autofocus': True,
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
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre

    def _post_clean(self):
        super()._post_clean()
        # Marca en rojo (clase Bootstrap is-invalid) los campos con errores
        for nombre_campo in self.errors:
            if nombre_campo in self.fields:
                widget = self.fields[nombre_campo].widget
                widget.attrs['class'] = f"{widget.attrs.get('class', '')} is-invalid".strip()


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
