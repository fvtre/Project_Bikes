from django.contrib import admin
from django.urls import path, include
from paypal.standard.ipn import urls as paypal_urls
from .views import *
from .models import Producto
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('actualizar_carrito/', actualizar_carrito, name='actualizar_carrito'),
    path('paypal/', include('paypal.standard.ipn.urls')),  # Esto agrega las rutas de PayPal IPN
    path('pago_paypal/', pago_paypal, name='pago_paypal'),
    path('pago_exitoso/', pago_exitoso, name='pago_exitoso'),
    path('pago_cancelado/', pago_cancelado, name='pago_cancelado'),
    path('pago_transferencia/', pago_transferencia, name='pago_transferencia'),
    path('carrito/', ver_carrito, name='carrito'),
    path('agregar_al_carrito/<int:producto_id>/', agregar_al_carrito, name='agregar_al_carrito'),
    path('eliminar/<int:item_id>/', eliminar_del_carrito, name='eliminar_del_carrito'),
    path('', inicio, name='inicio'),
    path('tienda/', tienda, name='tienda'),
    path('checkout/', tienda, name='checkout'),
    #crud contacto
    path('contacto/', contacto, name='contacto'),
    path('contacto_listar/', contacto_listar, name='contacto_listar'),
    path('contacto/<int:id>/', contacto_detalle, name='contacto_detalle'),
    path('contacto/<int:id>/editar/', contacto_editar, name='contacto_editar'),
    path('contacto/<int:id>/eliminar/', contacto_eliminar, name='contacto_eliminar'),
    path('ingresar/', ingresar, name='ingresar'),
    path('inicio_intra/', ingresar_intra, name='inicio_intra'),
    path('venta/', venta, name='venta'),
    path('servicio_tecnico/', servicio_tecnico, name='servicio_tecnico'),
    path('mantenedor_usuarios/', mantenedor_usuarios, name='mantenedor_usuarios'),
    path('mantenedor_productos/', mantenedor_productos, name='mantenedor_productos'),
    path('productos/<int:pk>/', detalle_producto, name='productos_detalle'),
    path('productos/actualiza/<int:pk>/', actualizar_producto, name='productos_actualiza'),
    path('productos/elimina/<int:pk>/', eliminar_producto, name='productos_eliminar'),
    path('productos/agregar/', agregar_producto, name='productos_nuevo'),
    # URLs para crud bicicletas
    path('bicicletas/', mantenedor_bicicletas, name='mantenedor_bicicletas'),
    path('bicicletas/nuevo/', agregar_bicicleta, name='agregar_bicicleta'),
    path('bicicletas/<int:pk>/', detalle_bicicleta, name='detalle_bicicleta'),
    path('bicicletas/<int:pk>/editar/', actualizar_bicicleta, name='actualizar_bicicleta'),
    path('bicicletas/<int:pk>/eliminar/', eliminar_bicicleta, name='eliminar_bicicleta'),
    # URLs para crud clientes
    path('clientes/', mantenedor_clientes, name='mantenedor_clientes'),
    path('clientes/nuevo/', agregar_cliente, name='agregar_cliente'),
    path('clientes/<int:pk>/', detalle_cliente, name='detalle_cliente'),
    path('clientes/<int:pk>/editar/', actualizar_cliente, name='actualizar_cliente'),
    path('clientes/<int:pk>/eliminar/', eliminar_cliente, name='eliminar_cliente'),
    # URLs para crud Arriendo
    path('arriendos/', mantenedor_arriendos, name='mantenedor_arriendos'),
    path('arriendos/agregar/', agregar_arriendo, name='agregar_arriendo'),
    path('arriendos/<int:pk>/', detalle_arriendo, name='detalle_arriendo'),
    path('arriendos/<int:pk>/actualizar/', actualizar_arriendo, name='actualizar_arriendo'),
    path('arriendos/<int:pk>/eliminar/', eliminar_arriendo, name='eliminar_arriendo'),
    path('salir/', salir, name='salir'),
    
    path('ventas/', listar_ventas, name='ventas_listar'),
    path('ventas/agregar/', agregar_venta, name='ventas_agregar'),
    path('ventas/<int:pk>/', detalle_venta, name='ventas_detalle'),
    path('ventas/<int:pk>/actualizar/', actualizar_venta, name='ventas_actualizar'),
    path('ventas/<int:pk>/eliminar/', eliminar_venta, name='ventas_eliminar'),
    
    # URLs para CRUD de Servicio
    path('servicios/', listar_servicios, name='listar_servicios'),
    path('servicios/agregar/', agregar_servicio, name='servicio_agregar'),
    path('servicios/<int:pk>/', detalle_servicio, name='servicio_detalle'),
    path('servicios/<int:pk>/actualizar/', actualizar_servicio, name='servicio_actualizar'),
    path('servicios/<int:pk>/eliminar/', eliminar_servicio, name='servicio_eliminar'),
    
    path('ventas/agregar/<int:producto_id>/', agregar_venta_directa, name='agregar_venta_directa'),
    path('registro/', registrar_cliente, name='registro'),
    path('success/', success, name='success'),  # Ruta para la página de éxito
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='inicio.html'),
    path('redirect-user/', redirect_user, name='redirect_user'),
    path('mis-pedidos/', mis_pedidos, name='mis_pedidos'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)