from django import forms
from .models import *
from .models import Producto



class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['categoria', 'name', 'descripcion', 'marca', 'modelo', 'color', 'stock', 'precio', 'imagen','destacado']
        
class BicicletaForm(forms.ModelForm):
    class Meta:
        model = Bicicleta
        fields = ['marca', 'modelo', 'aro', 'color', 'imagen']
        
class ClienteForm(forms.ModelForm):
    contraseña = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Cliente
        fields = ['usuario', 'nombre', 'contraseña', 'direccion', 'telefono', 'email', 'imagen']
        

class Clienteautoform(forms.ModelForm):
    contraseña = forms.CharField(widget=forms.PasswordInput(), label="Contraseña")
    repetir_contraseña = forms.CharField(widget=forms.PasswordInput(), label="Repetir Contraseña")

    class Meta:
        model = Cliente
        fields = ['usuario', 'nombre', 'direccion', 'telefono', 'email', 'imagen']

    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario')
        if User.objects.filter(username=usuario).exists():
            raise forms.ValidationError("El nombre de usuario ya está en uso.")
        return usuario

    def clean(self):
        cleaned_data = super().clean()
        contraseña = cleaned_data.get("contraseña")
        repetir_contraseña = cleaned_data.get("repetir_contraseña")

        if contraseña and repetir_contraseña and contraseña != repetir_contraseña:
            self.add_error('repetir_contraseña', "Las contraseñas no coinciden")

        return cleaned_data

class  ArriendoForm(forms.ModelForm):
    class Meta:
        model = Arriendo
        fields = ['bicicleta', 'cliente', 'fecha_inicio', 'fecha_fin', 'precio_por_dia']

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        if fecha_inicio and fecha_fin:
            if fecha_inicio >= fecha_fin:
                self.add_error('fecha_fin', 'La fecha de fin debe ser posterior a la fecha de inicio.')

        return cleaned_data

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        exclude = ['fecha_venta', 'total']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.all()

        if 'producto' in self.data:
            try:
                producto_id = int(self.data.get('producto'))
                producto = Producto.objects.get(id=producto_id)
                self.fields['precio_unitario'].initial = producto.precio
            except (ValueError, Producto.DoesNotExist):
                pass

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = '__all__'  # Puedes personalizar los campos aquí si es necesario
        
        
class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        fields = ['nombre', 'email', 'telefono', 'mensaje']
        

class CantidadCompraForm(forms.Form):
    cantidad = forms.IntegerField(min_value=1, label="Cantidad")
    nombre = forms.CharField(max_length=255, label="Nombre")
    telefono = forms.CharField(max_length=15, label="Teléfono")
    direccion = forms.CharField(max_length=255, label="Dirección")
    email = forms.EmailField(label="Email")