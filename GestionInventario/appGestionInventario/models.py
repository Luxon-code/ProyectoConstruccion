from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
# Create your models here.
estadosMantenimiento = [
    ('Satisfactorio','Satisfactorio'),('Requiere Ajuste','Requiere Ajuste'),
    ('Requiere Reparación','Requiere Reparación'),('Requiere Remplazo','Requiere Remplazo'),
    ('Defecto Corregido','Defecto Corregido'),
]
tipoProveedor = [
    ('Persona Júridica',"Persona Júridica"),('Persona Natural', 'Persona Natural'),
]
tipoUsuario = [
    ('Aprendiz',"Aprendiz"),('Instructor', 'Instructor'),('Administrativo',"Administrativo"),
]
tipoElemento = [
    ('HER','Herramientas'),('MAQ','Maquinaria'),('EQU','Equipos'),('MAT','Materiales'),  
]
estadosElementos = [
    ('Bueno','Bueno'),('Regular','Regular'),('Malo','Malo'),    
]
estadoSolicitudes = [
    ('Solicitada','Solicitada'),('Aprobada','Aprobada'),('Rechazada','Rechazada'),
    ('Atendida','Atendida'),('Cancelada','Cancelada')
]

class Ficha(models.Model):
    ficCodigo = models.IntegerField(unique=True,db_comment="Código de la Ficha")
    ficNombre = models.CharField(max_length=100,db_comment="Nombre del programa de la Ficha")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,
                                              db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,
                                                  db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.ficCodigo} - {self.ficNombre}"
    
class UnidadMedida(models.Model):
    uniNombre = models.CharField(max_length=45,unique=True,
                                 db_comment="Nombre de la Unidad de Médida")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,
                                              db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,
                                                  db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.uniNombre}"
   
class Proveedor(models.Model):
    proTipo  = models.CharField(max_length=20,choices=tipoProveedor,db_comment="Tipo de proveedor")
    proIdentificacion = models.CharField(max_length=15, unique=True,
                                         db_comment="Identificación del proveedor, puede ser cédula o Nit")
    proNombre = models.CharField(max_length=60,db_comment="Nombre del proveedor")    
    proRepresentanteLegal = models.CharField(max_length=60,null=True,
                                             db_comment="Nombre representante legal si es persona Júridica")    
    proTelefono = models.CharField(max_length=15, null=True,db_comment="Número telefono del proveedor")    
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.proNombre}"
    
class User(AbstractUser):
    userFoto = models.FileField(upload_to=f"fotos/", null=True, blank=True,db_comment="Foto del Usuario")
    userTipo = models.CharField(max_length=15,choices=tipoUsuario,db_comment="Nombre Tipo de usuario")
    email = models.EmailField(("email address"), blank=True,unique=True)
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self):
        return f"{self.username}"
    
class Elemento(models.Model):
    eleCodigo = models.CharField(max_length=15, unique=True,db_comment="Código único asignado al elemento")    
    eleNombre = models.CharField(max_length=50, db_comment="Nombre del Elemento")    
    eleTipo = models.CharField(max_length=3, choices=tipoElemento,db_comment="Tipo de Elemento")    
    eleEstado = models.CharField(max_length=10,choices=estadosElementos,
                                 db_comment="Estado del elemento devolutivo")    
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.eleCodigo}-{self.eleNombre}"
    
class Devolutivo(models.Model):
    devPlacaSena = models.CharField(max_length=45, unique=True,db_comment="Código Inventario SENA")
    devSerial = models.CharField(max_length=45, null=True,db_comment="Seríal del elemento devolutivo")
    devDescripcion  =models.TextField(db_comment="Descripción del elemento devolutivo")    
    devMarca = models.CharField(max_length=50,null=True,db_comment="Marca del Elemento Devolutivo")
    devFechaIngresoSENA = models.DateField(db_comment="Fecha de ingreso del elemento al inventario SENA")    
    devValor = models.DecimalField(max_digits=11, decimal_places=2,
                                   db_comment="Valor del elemento registrado inventario SENA")    
    devFoto = models.FileField(upload_to=f"elementos/", null=True, blank=True,
                                db_comment="Foto del Elemento Devolutivo")    
    devElemento = models.ForeignKey(Elemento,on_delete=models.PROTECT,db_comment="Hace relación al elemento FK")    
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.devElemento}"

class Material(models.Model):
    matReferencia = models.TextField(null=True,db_comment="Referencia o descripción del material")
    matMarca = models.CharField(max_length=50, null=True,db_comment="Marca del material si tiene")
    matElemento = models.ForeignKey(Elemento,on_delete=models.PROTECT,db_comment="Hace referencia al Elemento FK")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.matElemento}"
    
class EntradaMaterial(models.Model):
    entNumeroFactura = models.CharField(max_length=15,db_comment="Número de la factura")
    entUsuarioRecibe = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,
                                         db_comment="Hace referencia a usuario de construcción que recibe")
    entFechaHora = models.DateTimeField(default=timezone.now(),db_comment="Fecha y hora que entregan los elementos")
    entEntregadoPor = models.CharField(max_length=100,db_comment="Nombre persona que entrega los materiales")
    entObservaciones = models.TextField(null=True,db_comment="Observaciones que se requieran hacer")
    entProveedor = models.ForeignKey(Proveedor,on_delete=models.PROTECT,
                                     db_comment="Hace referencia al proveedor que entrea los materiales")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.entNumeroFactura}"
    
class DetalleEntradaMaterial(models.Model):
    detEntradaMaterial = models.ForeignKey(EntradaMaterial, on_delete=models.PROTECT,
                        db_comment="Hace referencia a la Entrada registrada")
    detMaterial = models.ForeignKey(Material, on_delete=models.PROTECT,
                        db_comment="Hace referencia al material que se está registrando en la entrada")
    detCantidad=models.IntegerField(db_comment="Cantidad que ingresa del material")
    detUnidadMedida = models.ForeignKey(UnidadMedida,on_delete=models.PROTECT,default=None,
                                        db_comment="Hace referencia a la Unidad de Medida FK")
    detPrecioUnitario = models.IntegerField(db_comment="Precio del material que ingresa")
    detEstado = models.CharField(max_length=7,choices=estadosElementos,db_comment="estado del Elemento")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.detMaterial} -> {self.detCantidad}"
    
class SolicitudElemento(models.Model):
    solUsuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,
                                db_comment="Usuario instructor que hace la solicitud")
    solFicha = models.ForeignKey(Ficha,on_delete=models.PROTECT,
                                 db_comment="Ficha en la que el instructor utilizará los elementos")
    solProyecto = models.TextField(db_comment="Nombre proyecto que el instructor está desarrollando con la ficha")
    solFechaHoraRequerida = models.DateTimeField(null=True,db_comment="Fecha y hora que requiere los elementos")
    solFechaHoraDevolver = models.DateTimeField(null=True,db_comment="Fecha y hora que devuelve los elementos")
    solEstado = models.CharField(max_length=10,choices=estadoSolicitudes,db_comment="Estado de la solicitud")
    solObservaciones = models.TextField(null=True,
                         db_comment="Alguna observación que el instructor quiera agregar en la solicitud")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.solUsuario}-{self.solFicha}-{self.solProyecto}"
    
class DetalleSolicitud(models.Model):
    detSolicitud = models.ForeignKey(SolicitudElemento,on_delete=models.PROTECT,
                                    db_comment="Hace referencia a la solicitud del detalle que se va a registrar")
    detElemento = models.ForeignKey(Elemento,on_delete=models.PROTECT,db_comment="Elemento que se está solicitando")    
    detUnidadMedida = models.ForeignKey(UnidadMedida,on_delete=models.PROTECT, null=True,
                                        db_comment="Unidad de médida del elemento que se requeire")
    detCantidadRequerida = models.IntegerField(db_comment="Cantidad requerida del elemento")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.detElemento}->{self.detCantidadRequerida}"
    
class SalidaDetalleSolicitud(models.Model):
    salDetalleSolicitud = models.ForeignKey(DetalleSolicitud,on_delete=models.PROTECT,
                                    db_comment="Hace referencia al detalle de la solicitud")
    salCantidadEntregada = models.IntegerField(db_comment="Cantidad entregada")
    salObservaciones = models.TextField(null=True, db_comment="Observaciobes que el asistente quiera agregar")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.salDetalleSolicitud}->{self.salCantidadEntregada}"
    
class DevolucionElemento(models.Model):
    devSalida = models.ForeignKey(SalidaDetalleSolicitud,on_delete=models.PROTECT,
                                  db_comment="Hace referencia a la salida de los elementos")
    devUsuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,
                                   db_comment="Usuario que hace la devolución de elementos")
    devCantidadDevolucion = models.IntegerField(db_comment="Cantidad devuelta por el instructor después \
                                    de utilizarla en la formación")
    devObservaciones = models.TextField(null=True, db_comment="Observaciones que el asistente quiera \
                                    agregar en la devolución")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.devSalida} -> {self.devCantidadDevolucion}"
    
    
class EstadoMantenimiento(models.Model):
    estNombre = models.CharField(max_length=50,unique=True,choices=estadosMantenimiento,
                                  db_comment="Nombre del estado del mantenimiento")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
        
    def __str__(self)->str:
        return f"{self.estNombre}"
    
class Mantenimento(models.Model):
    manElemento = models.ForeignKey(Elemento,on_delete=models.PROTECT,
                                db_comment="Hace referencia al elemento que se le realizó el mantenimiento")
    manUsuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,
                                db_comment="Hace referencia al usuario que realizó el mantenimiento")
    manEstado = models.ForeignKey(EstadoMantenimiento,on_delete=models.PROTECT,
                                db_comment="Hace referencia al estado del mantenimiento")
    manObservaciones = models.TextField(null=True,  db_comment="Observaciones que se quieran agregar \
                                al mantenimiento")
    manFechaHoraMantenimiento = models.DateTimeField(db_comment="Hace referencia a la fecha y hora que \
                                se realizó el mantenimiento")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.manElemento}-{self.manEstado}"
    
class UbicacionFisica(models.Model):
    ubiElemento  = models.ForeignKey(Elemento,on_delete=models.PROTECT,db_comment="Hace referencia al elemento")
    ubiDeposito = models.SmallIntegerField(db_comment="Número de bodega: 1,2,3,4..")    
    ubiEstante = models.SmallIntegerField(null=True,db_comment="Número de bodega: 1,2,3,4..")
    ubiEntrepano = models.SmallIntegerField(null=True,db_comment="Número de Entrepaño: 1,2,3,4..")
    ubiLocker = models.SmallIntegerField(null=True,db_comment="Número de locker: 1,2,3,4..")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.ubiElemento}-{self.ubiDeposito}-{self.ubiEstante}-{self.ubiEntrepano}-{self.ubiLocker}"
    
