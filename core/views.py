from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import admin_required, staff_required, customer_required
from django.contrib.auth.models import User, Group
from django.db import IntegrityError
from datetime import datetime
from django.db.models import Sum
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
import uuid
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from .models import Boleta, BoletaItem
from .forms import TipoEntregaForm
from .models import Notificacion



# Create your views here.

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


@staff_required
def listar_ventas_boletas(request):
    # Obtenemos todas las boletas con sus ventas
    boletas = Boleta.objects.prefetch_related('items')  # Prefetch de los items relacionados
    return render(request, 'core/ventas_listar.html', {'boletas': boletas})

@csrf_exempt
def actualizar_carrito(request):
    if request.method == "POST":
        data = json.loads(request.body)

        # Extraer información del pedido desde los datos enviados
        order_id = data.get('orderID')
        payment_details = data.get('details')

        if not order_id or not payment_details:
            return JsonResponse({"error": "Datos incompletos"}, status=400)

        # Procesar los elementos del carrito
        items = CarritoItem.objects.filter(usuario=request.user)
        for item in items:
            producto = item.producto

            # Verificar stock
            if producto.stock >= item.cantidad:
                producto.stock -= item.cantidad
                producto.save()
            else:
                return JsonResponse({"error": f"Stock insuficiente para {producto.nombre}"}, status=400)

        # Vaciar el carrito después del pago
       

        # Opcional: guardar los detalles del pago en una base de datos de historial
        # Payment.objects.create(user=request.user, order_id=order_id, amount=total, ...)

        return JsonResponse({"success": "Pago procesado correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)

def pago_paypal(request):
    items = CarritoItem.objects.filter(usuario=request.user)
    total = sum(item.producto.precio * item.cantidad for item in items)
    for item in items:
        item.subtotal = item.producto.precio * item.cantidad
    # Datos para PayPal
    paypal_dict = {
        "business": "tu_email_de_paypal@example.com",
        "amount": "100.00",  # Cambia esto por el total del carrito
        "item_name": "Compra en FerreMas",
        "invoice": "12345",  # Genera un número único para cada transacción
        "currency_code": "CLP",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return_url": request.build_absolute_uri(reverse('pago_exitoso')),
        "cancel_return": request.build_absolute_uri(reverse('pago_cancelado')),
    }
    
    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, "core/pago_paypal.html", {"form": form, 'items': items, 'total': total})

def pago_exitoso(request):
    if request.method == "GET":
        items = CarritoItem.objects.filter(usuario=request.user)

        if not items.exists():
            return render(request, "core/error_carrito_vacio.html")  # Manejo de carrito vacío

        # Crear la boleta
        numero_boleta = get_random_string(length=10)  # Generar un número único para la boleta
        boleta = Boleta.objects.create(
            usuario=request.user,
            numero_boleta=numero_boleta
        )

        # Agregar los items del carrito a la boleta
        for item in items:
            producto = item.producto

            # Verificar el stock
            if producto.stock >= item.cantidad:
                # Descontar el stock
                producto.stock -= item.cantidad
                producto.save()

                # Crear el BoletaItem
                BoletaItem.objects.create(
                    boleta=boleta,
                    producto=producto,
                    cantidad=item.cantidad
                )
            else:
                # Si no hay suficiente stock
                return render(request, "core/error_stock.html", {"producto": producto})

        # Calcular el total de la boleta
        boleta.calcular_total()

        # Eliminar los items del carrito
        items.delete()

        # Si es un GET, renderizar la página con el formulario
        form = TipoEntregaForm()
        return render(request, "core/pago_exitoso.html", {"boleta": boleta, "form": form})

    elif request.method == "POST":
        # Procesar el formulario
        form = TipoEntregaForm(request.POST)
        if form.is_valid():
            tipo_entrega = form.cleaned_data["tipo_entrega"]
            direccion_envio = form.cleaned_data["direccion_envio"] if tipo_entrega == "envio" else None

            # Recuperar la boleta usando el número enviado desde el formulario
            numero_boleta = request.POST.get("numero_boleta")
            try:
                boleta = Boleta.objects.get(numero_boleta=numero_boleta, usuario=request.user)
            except Boleta.DoesNotExist:
                return render(request, "core/error.html", {"mensaje": "Boleta no encontrada."})

            # Crear la notificación
            Notificacion.objects.create(
                boleta=boleta,
                tipo_entrega=tipo_entrega,
                direccion_envio=direccion_envio,
                nombre_comprador=request.user.username,
                apellido_comprador=request.user.last_name
            )

            # Redirigir al inicio o a otra página
            return redirect("inicio")

        # Si el formulario no es válido, recargar la página con los errores
        return render(request, "core/pago_exitoso.html", {"boleta": boleta, "form": form})

    
def pago_cancelado(request):
    return render(request, 'core/pago_cancelado.html')

def pago_transferencia(request):
    # Simula datos de ejemplo de transferencia bancaria
    datos_transferencia = {
        'banco': 'Banco Ejemplo',
        'numero_cuenta': '1234567890',
        'titular': 'Nombre del Titular',
        'referencia': 'TuReferenciaUnica',  # Podrías generar esto dinámicamente
        'total': request.session.get('total', 0),  # Obtén el total de la sesión o pásalo desde el carrito
    }
    return render(request, 'core/pago_transferencia.html', datos_transferencia)


@login_required
def mis_pedidos(request):
    # Filtrar notificaciones del cliente logueado por nombre y apellido
    notificaciones = Notificacion.objects.filter(
        nombre_comprador=request.user.first_name,
        apellido_comprador=request.user.last_name
    )
    return render(request, 'core/mis_pedidos.html', {'notificaciones': notificaciones})

@login_required
def ver_carrito(request):
    items = CarritoItem.objects.filter(usuario=request.user)
    total = sum(item.producto.precio * item.cantidad for item in items)
    for item in items:
        item.subtotal = item.producto.precio * item.cantidad  # Calcula subtotales para la plantilla
    return render(request, 'core/carrito.html', {'items': items, 'total': total })


@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    item, created = CarritoItem.objects.get_or_create(
        usuario=request.user,
        producto=producto,
        defaults={'cantidad': 1}
    )
    if not created:
        item.cantidad += 1
        item.save()
    return redirect('carrito')  # Use the URL name, not the template path

@login_required
def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)
    item.delete()
    return redirect('carrito')  # Use the URL name, not the template path

def contar_items(request):
    if request.user.is_authenticated:
        cantidad_productos = CarritoItem.objects.filter(usuario=request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
    else:
        cantidad_productos = 0
    return cantidad_productos


#clientes nuevos

def inicio(request):
    # Inicializamos cliente como None
    cliente = None

    # Verificamos si el usuario está autenticado
    if request.user.is_authenticated:
        try:
            # Obtenemos el cliente asociado al usuario
            cliente = Cliente.objects.get(usuario=request.user.username)
        except Cliente.DoesNotExist:
            # Maneja el caso en que el cliente no existe
            cliente = None

    # Filtramos los productos destacados
    productos_destacados = Producto.objects.filter(destacado=True)
    # Verificamos si se están obteniendo productos
    print(f"Productos destacados encontrados: {productos_destacados.count()}")

    # Renderizamos la plantilla con cliente y productos destacados en el contexto
    return render(request, 'core/inicio.html', {
        'cliente': cliente,
        'productos_destacados': productos_destacados,
    })


def checkout(request):
    return render(request, 'core/checkout.html')

def tienda(request):
    productos = Producto.objects.all()
    return render(request, 'core/tienda.html', {'productos': productos})

#autoregistro

def registrar_cliente(request):
    if request.method == 'POST':
        form = Clienteautoform(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Guardar el formulario de cliente
                cliente = form.save(commit=False)
                
                # Crear un nuevo usuario
                usuario = User.objects.create_user(username=form.cleaned_data['usuario'], password=form.cleaned_data['contraseña'])
                
                # Asignar el usuario al cliente
                cliente.usuario = usuario.username
                cliente.contraseña = form.cleaned_data['contraseña']
                
                # Guardar el cliente
                cliente.save()
                
                messages.success(request, "¡Registro exitoso! Ahora puedes iniciar sesión.")
                return redirect('success')  # Asegúrate de que 'success' es una URL válida en tu proyecto

            except IntegrityError:
                messages.error(request, "Error de integridad: El nombre de usuario ya está en uso.")
    else:
        form = Clienteautoform()
    
    return render(request, 'core/registro.html', {'form': form})

def success(request):
    return render(request, 'core/success.html')

def contacto(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            form.save()
            # Agregar un mensaje de éxito
            mensaje = "¡Gracias por contactarnos! Nos pondremos en contacto contigo lo antes posible."
            return render(request, 'core/inicio.html', {'form': form, 'mensaje': mensaje})
    else:
        form = ContactoForm()
    
    return render(request, 'core/contacto.html', {'form': form})

@staff_required
def contacto_listar(request):
    contactos = Contacto.objects.all()
    return render(request, 'core/contacto_listar.html', {'contactos': contactos})

@staff_required
def contacto_detalle(request, id):
    contacto = get_object_or_404(Contacto, id=id)
    return render(request, 'core/contacto_detalle.html', {'contacto': contacto})

@staff_required
def contacto_editar(request, id):
    contacto = get_object_or_404(Contacto, id=id)
    if request.method == 'POST':
        form = ContactoForm(request.POST, instance=contacto)
        if form.is_valid():
            form.save()
            return redirect('contacto_listar')
    else:
        form = ContactoForm(instance=contacto)
    return render(request, 'core/contacto_editar.html', {'form': form})

@staff_required
def contacto_eliminar(request, id):
    contacto = get_object_or_404(Contacto, id=id)
    if request.method == 'POST':
        contacto.delete()
        return redirect('contacto_listar')
    return render(request, 'core/contacto_eliminar.html', {'contacto': contacto})

def ingresar(request):
    return render(request, 'core/ingresar.html')


#Colaborador registrado
@login_required
def ingresar_intra(request):
    return render(request, 'core/inicio_intra.html')

def venta(request):
    return render(request, 'core/venta.html')

def venta(request):
    return render(request, 'core/venta.html')

def servicio_tecnico(request):
    return render(request, 'core/servicio_tecnico.html')

def mantenedor_usuarios(request):
    return render(request, 'core/mantenedor_usuarios.html')

def salir(request):
    return render(request, 'core/salir.html')


#crud producto
#Listar
@staff_required
def mantenedor_productos(request):
    productos = Producto.objects.all()
    return render(request, 'core/mantenedor_productos.html', {'productos': productos})

#agregar
@staff_required
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('inicio_intra')
    else:
        form = ProductoForm()
    
    return render(request, 'core/productos_nuevo.html', {'form': form})

#ver detalle
@staff_required
def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'core/productos_detalle.html', {'producto': producto})

#actualiza
@staff_required
def actualizar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('inicio_intra')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'core/productos_actualiza.html', {'form': form})

#elimina
@staff_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('inicio_intra')
    
    return render(request, 'core/productos_eliminar.html', {'producto': producto})

#crud bicicleta
# Listar
@staff_required
def mantenedor_bicicletas(request):
    bicicletas = Bicicleta.objects.all()
    return render(request, 'core/mantenedor_bicicletas.html', {'bicicletas': bicicletas})

# Agregar
@staff_required
def agregar_bicicleta(request):
    if request.method == 'POST':
        form = BicicletaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('mantenedor_bicicletas')
    else:
        form = BicicletaForm()
    
    return render(request, 'core/bicicleta_nuevo.html', {'form': form})

# Ver detalle
@staff_required
def detalle_bicicleta(request, pk):
    bicicleta = get_object_or_404(Bicicleta, pk=pk)
    return render(request, 'core/bicicleta_detalle.html', {'bicicleta': bicicleta})

# Actualizar
@staff_required
def actualizar_bicicleta(request, pk):
    bicicleta = get_object_or_404(Bicicleta, pk=pk)
    if request.method == 'POST':
        form = BicicletaForm(request.POST, request.FILES, instance=bicicleta)
        if form.is_valid():
            form.save()
            return redirect('mantenedor_bicicletas')
    else:
        form = BicicletaForm(instance=bicicleta)
    
    return render(request, 'core/bicicleta_actualiza.html', {'form': form})

# Eliminar
@staff_required
def eliminar_bicicleta(request, pk):
    bicicleta = get_object_or_404(Bicicleta, pk=pk)
    if request.method == 'POST':
        bicicleta.delete()
        return redirect('mantenedor_bicicletas')
    
    return render(request, 'core/bicicleta_eliminar.html', {'bicicleta': bicicleta})

#crud clientes
# Listar
@staff_required
def mantenedor_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'core/mantenedor_clientes.html', {'clientes': clientes})

# Agregar
@admin_required
def agregar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('mantenedor_clientes')
    else:
        form = ClienteForm()
    
    return render(request, 'core/cliente_nuevo.html', {'form': form})

# Ver detalle
@admin_required
def detalle_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    return render(request, 'core/cliente_detalle.html', {'cliente': cliente})

# Actualizar
@admin_required
def actualizar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('mantenedor_clientes')
    else:
        form = ClienteForm(instance=cliente)
    
    return render(request, 'core/cliente_actualiza.html', {'form': form})

# Eliminar
@admin_required
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        return redirect('mantenedor_clientes')
    
    return render(request, 'core/cliente_eliminar.html', {'cliente': cliente})

#crud arriendos
#listar
@staff_required
def mantenedor_arriendos(request):
    arriendos = Arriendo.objects.all()
    return render(request, 'core/mantenedor_arriendos.html', {'arriendos': arriendos})

#agregar
@staff_required
def agregar_arriendo(request):
    if request.method == 'POST':
        form = ArriendoForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('mantenedor_arriendos')
            except ValidationError as e:
                form.add_error(None, e.message)
    else:
        form = ArriendoForm()
    
    return render(request, 'core/arriendo_nuevo.html', {'form': form})

#detalle arriendo 
@staff_required
def detalle_arriendo(request, pk):
    arriendo = get_object_or_404(Arriendo, pk=pk)
    return render(request, 'core/arriendo_detalle.html', {'arriendo': arriendo})

#actualiza arriendo
@staff_required
def actualizar_arriendo(request, pk):
    arriendo = get_object_or_404(Arriendo, pk=pk)
    if request.method == 'POST':
        form = ArriendoForm(request.POST, instance=arriendo)
        if form.is_valid():
            form.save()
            return redirect('mantenedor_arriendos')
    else:
        form = ArriendoForm(instance=arriendo)
    
    return render(request, 'core/arriendo_actualiza.html', {'form': form})

#elimina arriendo
@staff_required
def eliminar_arriendo(request, pk):
    arriendo = get_object_or_404(Arriendo, pk=pk)
    if request.method == 'POST':
        arriendo.delete()
        return redirect('mantenedor_arriendos')
    
    return render(request, 'core/arriendo_eliminar.html', {'arriendo': arriendo})

#crud ventas
# Listar todas las ventas
@staff_required
def listar_ventas(request):
    ventas = Venta.objects.all()
    return render(request, 'core/ventas_listar.html', {'ventas': ventas})

# Agregar una nueva venta
@staff_required
def agregar_venta(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ventas_listar')
    else:
        form = VentaForm()
    return render(request, 'core/ventas_agregar.html', {'form': form})

# Ver detalle de una venta específica
@staff_required
def detalle_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    return render(request, 'core/ventas_detalle.html', {'venta': venta})

# Actualizar una venta existente
@staff_required
def actualizar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == 'POST':
        form = VentaForm(request.POST, instance=venta)
        if form.is_valid():
            form.save()
            return redirect('ventas_listar')
    else:
        form = VentaForm(instance=venta)
    return render(request, 'core/ventas_actualizar.html', {'form': form})

# Eliminar una venta existente
@staff_required
def eliminar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == 'POST':
        venta.delete()
        return redirect('ventas_listar')
    return render(request, 'core/ventas_eliminar.html', {'venta': venta})

#crud servicio

# Listar todos los servicios
@staff_required
def listar_servicios(request):
    servicios = Servicio.objects.all()
    return render(request, 'core/listar_servicios.html', {'servicios': servicios})

# Agregar un nuevo servicio
@staff_required
def agregar_servicio(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listar_servicios')
    else:
        form = ServicioForm()
    return render(request, 'core/servicio_agregar.html', {'form': form})

# Ver detalle de un servicio específico
@staff_required
def detalle_servicio(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    return render(request, 'core/servicio_detalle.html', {'servicio': servicio})

# Actualizar un servicio existente
@staff_required
def actualizar_servicio(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES, instance=servicio)
        if form.is_valid():
            form.save()
            return redirect('listar_servicios')
    else:
        form = ServicioForm(instance=servicio)
    return render(request, 'core/servicio_actualizar.html', {'form': form, 'servicio': servicio})

# Eliminar un servicio existente
@staff_required
def eliminar_servicio(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        servicio.delete()
        return redirect('listar_servicios')
    return render(request, 'core/servicio_eliminar.html', {'servicio': servicio})


@login_required
def agregar_venta_directa(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    cliente = None

    if request.user.is_authenticated:
        # Obtener el cliente asociado al usuario logeado
        if hasattr(request.user, 'cliente'):
            cliente = request.user.cliente

    if request.method == 'POST':
        form = CantidadCompraForm(request.POST)
        if form.is_valid():
            cantidad = form.cleaned_data['cantidad']
            nombre = form.cleaned_data['nombre']
            telefono = form.cleaned_data['telefono']
            direccion = form.cleaned_data['direccion']
            email = form.cleaned_data['email']
            precio_unitario = producto.precio

            if cantidad > producto.stock:
                messages.error(request, f"La cantidad solicitada es mayor al stock disponible. Stock actual: {producto.stock}")
            else:
                # Reducir el stock del producto
                producto.stock -= cantidad
                producto.save()

                # Crear una nueva venta directamente
                venta = Venta(
                    producto=producto,
                    precio_unitario=precio_unitario,
                    cantidad=cantidad,
                    cliente=nombre,
                    direccion_envio=direccion,
                    telefono_contacto=telefono,
                    email_contacto=email
                )

                venta.save()

                # Mensaje de compra exitosa
                messages.success(request, f"¡Compra exitosa, {nombre}! Has comprado {producto.marca} {producto.modelo}")

                # Redirigir a donde desees después de agregar la venta
                return redirect('tienda')
        else:
            messages.error(request, "Hay errores en el formulario. Por favor, corrígelos.")
    else:
        form = CantidadCompraForm()

    return render(request, 'core/agregar_venta.html', {'form': form, 'producto': producto})


#redirige segun privilegios
def redirect_user(request):
    if request.user.groups.filter(name='customer').exists():
        return redirect('inicio')
    elif request.user.is_staff or request.user.is_superuser:
        return redirect('inicio_intra')
    else:
        return redirect('inicio')  # Redirección por defecto, si no cumple con ninguna condición