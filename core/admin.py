from django.contrib import admin
from .models import *
from django.contrib.auth.models import Group, Permission

# Registrar grupos y permisos

admin.site.register(Permission)

admin.site.register(Producto)
admin.site.register(Venta)
admin.site.register(Cliente)
admin.site.register(Bicicleta)
admin.site.register(Arriendo)
