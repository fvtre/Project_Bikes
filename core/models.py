from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from django.utils.crypto import get_random_string

# Create your models here.

class Producto(models.Model):
    categoria = models.CharField(
        max_length=100,
        choices=[
            ('seguridad', 'Seguridad'),
            ('casco', 'Casco'),
            ('guantes', 'Guantes'),
            ('ropa', 'Ropa'),
            ('goggles', 'Goggles'),
            ('otros', 'Otros'),
        ]
    )
    name = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    stock = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    destacado = models.BooleanField(default=False)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def __str__(self):
        return self.name

class Venta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    cliente = models.CharField(max_length=255)
    direccion_envio = models.CharField(max_length=255)
    telefono_contacto = models.CharField(max_length=15)
    email_contacto = models.EmailField()

    def save(self, *args, **kwargs):
        self.total = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Venta #{self.id} - {self.producto}"

class Cliente(models.Model):
    usuario = models.CharField(max_length=255, blank=True)
    nombre = models.CharField(max_length=255, blank=True)
    contraseña = models.CharField(max_length=255, blank=True)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15)
    email = models.EmailField()
    imagen = models.ImageField(upload_to='cliente/', null=True, blank=True)

    def __str__(self):
        return self.nombre


class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=15)
    mensaje = models.TextField()
    fecha_contacto = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.email}"

class Bicicleta(models.Model):
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    aro = models.IntegerField()
    color = models.CharField(max_length=100, blank=True)
    imagen = models.ImageField(upload_to='bicicletas/', null=True, blank=True)

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.aro})"


class Arriendo(models.Model):
    bicicleta = models.ForeignKey(Bicicleta, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    precio_por_dia = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Validar si la bicicleta está arrendada para las fechas especificadas
        if self.bicicleta.arriendo_set.filter(
            fecha_fin__gte=self.fecha_inicio,
            fecha_inicio__lte=self.fecha_fin
        ).exists():
            raise ValidationError(_('La bicicleta seleccionada ya está arrendada para las fechas especificadas.'))

        # Calcula la diferencia en días entre la fecha de inicio y fin
        duracion = (self.fecha_fin - self.fecha_inicio).days
        # Calcula el total en base a la duración y el precio por día
        self.total = duracion * self.precio_por_dia
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Arriendo #{self.id} - {self.bicicleta} por {self.cliente}"
    

class Servicio(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    bicicleta = models.CharField(max_length=100, blank=True)
    marca = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    descripcion = models.TextField()
    fecha_servicio = models.DateTimeField(auto_now_add=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    completado = models.BooleanField(default=False)
    imagen = models.ImageField(upload_to='servicio/', null=True, blank=True)

    def __str__(self):
        return f"Servicio para {self.cliente} en {self.fecha_servicio}"


class CarritoItem(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    def subtotal(self):
        return self.producto.precio * self.cantidad


class TransaccionPaypal(models.Model):
    payer_id = models.CharField(max_length=250)
    paymetn_date = models.DateTimeField()
    payment_status = models.CharField(max_length=250)
    quantity = models.IntegerField()
    invoice = models.CharField(max_length=250)
    first_name = models.CharField(max_length=250)
    payer_status = models.CharField(max_length=250)
    payer_email = models.CharField(max_length=250)
    txn_id = models.CharField(max_length=250)
    receiver_id = models.CharField(max_length=250)
    payment_gross = models.FloatField()
    custom = models.CharField(max_length=250)
    
    def _str_(self):
        return self.custom
    

class Boleta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    numero_boleta = models.CharField(max_length=20, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Boleta #{self.numero_boleta} - Usuario: {self.usuario.username}"

    def calcular_total(self):
        """Calcula el total de la boleta sumando los subtotales de los BoletaItems."""
        total = sum(item.subtotal() for item in self.boletaitem_set.all())
        self.total = total
        self.save()


class BoletaItem(models.Model):
    boleta = models.ForeignKey(Boleta, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        """Calcula el subtotal para este producto."""
        return self.producto.precio * self.cantidad

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} unidades"
    

def generar_boleta(usuario, items_carrito):
    # Crear una nueva boleta
    numero_boleta = get_random_string(length=10)  # Genera un número de boleta único
    boleta = Boleta.objects.create(usuario=usuario, numero_boleta=numero_boleta)

    # Agregar los items del carrito a la boleta
    for item in items_carrito:
        BoletaItem.objects.create(
            boleta=boleta,
            producto=item.producto,
            cantidad=item.cantidad
        )

    # Calcular el total de la boleta
    boleta.calcular_total()

    # Vaciar el carrito después de generar la boleta
    items_carrito.delete()

    return boleta