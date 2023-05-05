from django.contrib import admin
from appGestionInventario.models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Material)
admin.site.register(Elemento)
admin.site.register (Devolutivo) 
admin.site.register(DevolucionElemento)
admin.site.register(EntradaMaterial)
admin.site.register(DetalleEntradaMaterial)
admin.site.register(SolicitudElemento)
admin.site.register(DetalleSolicitud)
admin.site.register(SalidaDetalleSolicitud)
admin.site.register(Mantenimento)
admin.site.register(EstadoMantenimiento)
admin.site.register(Ficha)
admin.site.register(Proveedor)
admin.site.register(UbicacionFisica)
admin.site.register(UnidadMedida)
