from .views import contar_items

def carrito_contador(request):
    return {'cantidad_productos': contar_items(request)}