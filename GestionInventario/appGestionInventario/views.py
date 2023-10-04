from datetime import date, datetime
from django.shortcuts import render, redirect
from appGestionInventario.models import *
from django.contrib.auth.models import Group
from django.db import Error, transaction
import random
import string
from django.contrib.auth import authenticate
from django.contrib import auth
from django.conf import settings
import urllib
import json
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
import threading
from smtplib import SMTPException
from django.http import JsonResponse
from django.db.models import Sum, Avg, Count
import matplotlib.pyplot as plt
import os
from fpdf import FPDF
from appGestionInventario.pdfSolicitudes import PDF
# Create your views here.
datosSesion = {"user": None, "rutaFoto": None, "rol": None}


def inicioAdministrador(request):
    if request.user.is_authenticated:
        datosSesion = {"user": request.user,
                       "rol": request.user.groups.get().name}
        return render(request, "administrador/inicio.html", datosSesion)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})

def vistaGestionarCuenta(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Administrador').exists():
            retorno = {"user":request.user}  
            return render(request,'administrador/gestionarCuenta.html',retorno)
        elif request.user.groups.filter(name='Asistente').exists() :
            retorno = {"user":request.user}  
            return render(request,'asistente/gestionarCuenta.html',retorno)
        else:
            retorno = {"user":request.user}  
            return render(request,'instructor/gestionarCuenta.html',retorno) 
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})
    
def modificarDatosUserPerfil(request,id):
    """
    Modifica los datos de un usuario en su perfil y guarda los cambios en la base de datos.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        id (int): El ID del usuario cuyos datos se desean modificar.

    Returns:
        HttpResponse: Una respuesta HTTP que redirige al perfil del usuario con un mensaje de éxito o error.
    """
    if request.method == "POST":
        try:
            nombres = request.POST["txtNombres"]
            apellidos = request.POST["txtApellidos"]
            correo = request.POST["txtCorreo"]
            foto = request.FILES.get("fileFoto", False)
            with transaction.atomic():
                user = User.objects.get(pk=id)
                user.username=correo
                user.first_name=nombres
                user.last_name=apellidos
                user.email=correo
                if(foto):
                    if user.userFoto == "":
                        user.userFoto=foto
                    else:
                        os.remove('./media/'+str(user.userFoto))
                        user.userFoto=foto
                user.save()
                mensaje = "Datos Modificados Correctamente"
                retorno = {"mensaje": mensaje,"estado":True}
                if user.groups.filter(name='Administrador').exists():
                    return render(request,'administrador/gestionarCuenta.html',retorno)
                elif user.groups.filter(name='Asistente').exists() :
                    return render(request,'asistente/gestionarCuenta.html',retorno)
                else:
                    return render(request,'instructor/gestionarCuenta.html',retorno) 
        except Error as error:
            transaction.rollback()
            if 'user.username' in str(error):
                mensaje = "Ya existe un usuario con este correo electronico"
            elif 'user.email' in str(error):
                mensaje = "Ya existe un usuario con ese correo electronico"
            else:
                mensaje = error
        retorno = {"mensaje":mensaje,"estado":False}
        if user.groups.filter(name='Administrador').exists():
            return render(request,'administrador/gestionarCuenta.html',retorno)
        elif user.groups.filter(name='Asistente').exists() :
            return render(request,'asistente/gestionarCuenta.html',retorno)
        else:
            return render(request,'instructor/gestionarCuenta.html',retorno) 

def vistaRegistrarUsuario(request):
    if request.user.is_authenticated:
        roles = Group.objects.all()
        retorno = {"roles": roles, "user": request.user,
                   "rol": request.user.groups.get().name}
        return render(request, "administrador/frmRegistrarUsuario.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})


def registrarUsuario(request):
    try:
        nombres = request.POST["txtNombres"]
        apellidos = request.POST["txtApellidos"]
        correo = request.POST["txtCorreo"]
        tipo = request.POST["cbTipo"]
        foto = request.FILES.get("fileFoto")
        idRol = int(request.POST["cbRol"])
        with transaction.atomic():
            # crear un objeto de tipo User
            user = User(username=correo, first_name=nombres,
                        last_name=apellidos, email=correo, userTipo=tipo, userFoto=foto)
            user.save()
            # obtener el Rol de acuerdo a id del rol
            rol = Group.objects.get(pk=idRol)
            # agregar el usuario a ese Rol
            user.groups.add(rol)
            # si el rol es Administrador se habilita para que tenga acceso al sitio web del administrador
            if (rol.name == "Administrador"):
                user.is_staff = True 
            # guardamos el usuario con lo que tenemos
            user.save()
            # llamamos a la funcion generarPassword
            passwordGenerado = generarPassword()
            print(f"password {passwordGenerado}")
            # con el usuario creado llamamos a la función set_password que
            # # encripta el password y lo agrega al campo password del user.
            user.set_password(passwordGenerado)
            # se actualiza el user
            user.save()
            mensaje = "Usuario Agregado Correctamente"
            retorno = {"mensaje": mensaje}
            # enviar correo al usuario
            asunto = 'Registro Sistema Inventario CIES-NEIVA'
            mensaje = f'Cordial saludo, <b>{user.first_name} {user.last_name}</b>, nos permitimos.\
                informarle que usted ha sido registrado en el Sistema de Gestión de Inventario \
                del Centro de la Industria, la Empresa y los Servicios CIES de la ciudad de Neiva.\
                Nos permitimos enviarle las credenciales de Ingreso a nuestro sistema.<br>\
                <br><b>Username: </b> {user.username}\
                <br><b>Password: </b> {passwordGenerado}\
                <br><br>Lo invitamos a ingresar a nuestro sistema en la url:\
                http://gestioninventario.sena.edu.co.'
            thread = threading.Thread(
                target=enviarCorreo, args=(asunto, mensaje, [user.email]))
            thread.start()
            return redirect("/vistaGestionarUsuarios/", retorno)
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"
    retorno = {"mensaje": mensaje}
    return render(request, "administrador/frmRegistrarUsuario.html", retorno)


def generarPassword():
    """
    Genera un password de longitud de 10 que incluye letras mayusculas
    y minusculas,digitos y cararcteres especiales
    Returns:
        _str_: retorna un password
    """
    longitud = 10

    caracteres = string.ascii_lowercase + \
        string.ascii_uppercase + string.digits + string.punctuation
    password = ''

    for i in range(longitud):
        password += ''.join(random.choice(caracteres))
    return password

def cambiarEstadoUsuario(request,id):
    """
    Cambia el estado (activo/inactivo) de un usuario en el sistema y devuelve una respuesta JSON con el resultado.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.
        id (int): El ID del usuario cuyo estado se desea cambiar.

    Returns:
        JsonResponse: Una respuesta JSON que indica si el cambio de estado fue exitoso y contiene un mensaje correspondiente.
    """
    estado = False
    try:
        with transaction.atomic():
            user = User.objects.get(pk=id)
            if user.is_superuser:
                mensaje = "Este usuario no se le puede cambiar el estado, ya que es el superuser del sistema"
                estado = False
            else:
                if user.is_active:
                    user.is_active = False
                    mensaje = "Inactivo"
                else:
                    user.is_active = True
                    mensaje = "Activo"
                user.save()
                estado = True
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"
    retorno = {
        'estado': estado,
        'mensaje':mensaje
    }
    
    return JsonResponse(retorno)

def vistaGestionarUsuarios(request):
    if request.user.is_authenticated:
        usuarios = User.objects.all()
        retorno = {"usuarios": usuarios, "user": request.user,
                   "rol": request.user.groups.get().name}
        return render(request, "administrador/vistaGestionarUsuarios.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})


def vistaLogin(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Administrador').exists():
            return redirect('/inicioAdministrador')
        elif request.user.groups.filter(name='Asistente').exists():
            return redirect('/inicioAsistente')
        else:
            return redirect('/inicioInstructor')
    else:
        return render(request, "frmIniciarSesion.html")


def login(request):
    # validar el recapthcha
    """Begin reCAPTCHA validation"""
    recaptcha_response = request.POST.get('g-recaptcha-response')
    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }
    data = urllib.parse.urlencode(values).encode()
    req = urllib.request.Request(url, data=data)
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode())
    print(result)
    """ End reCAPTCHA validation """
    if result['success']:
        username = request.POST["txtUsername"]
        password = request.POST["txtPassword"]
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            # registrar la variable de sesión
            auth.login(request, user)
            if user.groups.filter(name='Administrador').exists():
                return redirect('/inicioAdministrador')
            elif user.groups.filter(name='Asistente').exists():
                return redirect('/inicioAsistente')
            else:
                return redirect('/inicioInstructor')
        else:
            mensaje = "Usuario o Contraseña Incorrectas"
            return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})
    else:
        mensaje = "Debe validar primero el recaptcha"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})


def salir(request):
    auth.logout(request)
    return render(request, "frmIniciarSesion.html",
                  {"mensaje": "Ha cerrado la sesión"})


def SolicitarElementos(request):
    hoy = date.today()
    json = {
        "hoy": hoy.strftime("%Y-%m-%dT%H:%M"),
        "fichas": Ficha.objects.all(),
        "rol": request.user.groups.get().name,
    }
    return render(request, "instructor/solicitarElementos.html", json)


def enviarCorreo(asunto=None, mensaje=None, destinatario=None,archivo=None):
    remitente = settings.EMAIL_HOST_USER
    template = get_template('enviarCorreo.html')
    contenido = template.render({
        'destinatario': destinatario,
        'mensaje': mensaje,
        'asunto': asunto,
        'remitente': remitente,
    })
    try:
        correo = EmailMultiAlternatives(
            asunto, mensaje, remitente, destinatario)
        correo.attach_alternative(contenido, 'text/html')
        if archivo != None:
            correo.attach_file(archivo)
        correo.send(fail_silently=True)
    except SMTPException as error:
        print(error)


def vistaGestionarElementos(request):
    if request.user.is_authenticated:
        retorno = {"devolutivos": Devolutivo.objects.all(),
                   "ubicaciones": UbicacionFisica.objects.all(),
                   "user": request.user, "rol": request.user.groups.get().name}
        return render(request, "asistente/vistaGestionarElementos.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})


def vistaRegistrarElementos(request):
    if request.user.is_authenticated:
        retorno = {"tipoElemento": tipoElemento, "estadoElemento": estadosElementos, "user": request.user,
                   "rol": request.user.groups.get().name}
        return render(request, "asistente/frmRegistrarElementos.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})


def registrarElementos(request):
    estado = False
    try:
        # datos del elemento en general
        nombreEle = request.POST['txtNombre']
        tipoEle = request.POST['cbTipo']
        estadoEle = request.POST['cbEstado']
        # datos del devolitivo
        placaSena = request.POST['txtPlacaSena']
        serial = request.POST['txtSerial']
        marca = request.POST['txtMarca']
        descripcion = request.POST['txtDescripcion']
        fechaIngreso = request.POST['txtFecha']
        valor = float(request.POST['txtValor'])
        foto = request.FILES.get('fileFoto', False)
        # datos de la ubucacion fisica
        deposito = request.POST['txtDesposito']
        estante = request.POST.get('txtEstante', False)
        if estante == "":
            estante = 0
        entrepaño = request.POST.get('txtEntrepaño', False)
        if entrepaño == "":
            entrepaño = 0
        loker = request.POST.get('txtLoker', False)
        if loker == "":
            loker = 0
        with transaction.atomic():
            # obtener cuantos elementos se han registrado
            cantidad = Elemento.objects.all().count()
            # crear un codigo a partir de la cantidad, ajustando 0 al inicio
            codigoElemento = tipoEle.upper() + str(cantidad+1).rjust(5, '0')
            # crear el elemento
            elemento = Elemento(
                eleCodigo=codigoElemento, eleNombre=nombreEle, eleTipo=tipoEle, eleEstado=estadoEle)
            # salvar el elemento en la base de datos
            elemento.save()
            # crear objeto ubicación física del elemento
            ubicacion = UbicacionFisica(ubiElemento=elemento, ubiDeposito=deposito, ubiEstante=estante, ubiEntrepano=entrepaño,
                                        ubiLocker=loker)
            # registrar en la base de datos la ubicación física del elemento
            ubicacion.save()
            # crear el devolutivo
            devolutivo = Devolutivo(devPlacaSena=placaSena, devSerial=serial, devDescripcion=descripcion,
                                    devMarca=marca, devFechaIngresoSENA=fechaIngreso, devValor=valor,
                                    devFoto=foto, devElemento=elemento)
            # registrar el elemento en la base de datos
            devolutivo.save()
            estado = True
            mensaje = f"Elemento Devolutivo registrado Satisfactoriamente con el codigo {codigoElemento}"
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"
    retorno = {"mensaje": mensaje, "devolutivo": devolutivo, "estado": estado, "tipoElemento": tipoElemento,
               "estadoElemento": estadosElementos, "ubicacionFisica": ubicacion}
    return render(request, "asistente/frmRegistrarElementos.html", retorno)


def asistenteInicio(request):
    if request.user.is_authenticated:
        datosSesion = {"user": request.user,
                       "rol": request.user.groups.get().name}
        return render(request, "asistente/inicio.html", datosSesion)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})


def asistenteSolicitudes(request):
    if request.user.is_authenticated:
        retorno = {"user": request.user,
                   "rol": request.user.groups.get().name,
                   'solicitudes': SolicitudElemento.objects.filter(solEstado='Aprobada').all(),}
        return render(request, "asistente/SolicitudesAprobadas.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})


def vistaGestionarMateriales(request):
    if request.user.is_authenticated:
        retorno = {"materiales": Material.objects.all(),
                   "user": request.user,
                   "ubicaciones": UbicacionFisica.objects.all(),
                   "rol": request.user.groups.get().name}
        return render(request, "asistente/vistaGestionarMateriales.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})


def vistaRegistrarMateriales(request):
    if request.user.is_authenticated:
        retorno = {"estadoElemento": estadosElementos, "user": request.user,
                   "rol": request.user.groups.get().name}
        return render(request, "asistente/frmRegistrarMateriales.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})


def registrarMaterial(request):
    estado = False
    try:
        # datos del elemento en general
        nombreEle = request.POST['txtNombre']
        estadoEle = request.POST['cbEstado']
        # datos del elemento material
        referencia = request.POST.get('txtReferencia', None)
        marca = request.POST.get('txtMarca', None)
        # datos de la ubucacion fisica
        deposito = request.POST['txtDesposito']
        estante = request.POST.get('txtEstante', False)
        if estante == "":
            estante = 0
        entrepaño = request.POST.get('txtEntrepaño', False)
        if entrepaño == "":
            entrepaño = 0
        loker = request.POST.get('txtLoker', False)
        if loker == "":
            loker = 0
        with transaction.atomic():
            # obtener cuantos elementos se han registrado
            cantidad = Elemento.objects.all().filter(eleTipo="MAT").count()
            # crear un codigo a partir de la cantidad, ajustando 0 al inicio
            codigoElemento = "MAT" + str(cantidad+1).rjust(5, '0')
            # crear el elemento
            elemento = Elemento(
                eleCodigo=codigoElemento, eleNombre=nombreEle, eleTipo="MAT", eleEstado=estadoEle)
            # salvar el elemento en la base de datos
            elemento.save()
            # crear objeto ubicación física del elemento
            ubicacion = UbicacionFisica(ubiElemento=elemento, ubiDeposito=deposito, ubiEstante=estante, ubiEntrepano=entrepaño,
                                        ubiLocker=loker)
            # registrar en la base de datos la ubicación física del elemento
            ubicacion.save()
            # crear el objeto Material
            material = Material(matReferencia=referencia,
                                matMarca=marca, matElemento=elemento)
            material.save()
            estado = True
            mensaje = f"Elemento Material registrado Satisfactoriamente con el codigo {codigoElemento}"
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"
    retorno = {"mensaje": mensaje, "estado": estado,
               "estadoElemento": estadosElementos, "unidadesMedidas": UnidadMedida.objects.all(),
               "material": material, "ubicacionFisica": ubicacion}
    return render(request, "asistente/frmRegistrarMateriales.html", retorno)


def inicioInstructor(request):
    if request.user.is_authenticated:
        datosSesion = {"user": request.user,
                       "rol": request.user.groups.get().name}
        return render(request, "instructor/inicio.html", datosSesion)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})


def vistaRegistrarEntradaMaterial(request):
    if request.user.is_authenticated:
        hoy = date.today()
        retorno = {
            "materiales": Material.objects.all(),
            "unidadesMedida": UnidadMedida.objects.all(),
            "usuarios": User.objects.all(),
            "proveedores": Proveedor.objects.all(),
            "user": request.user,
            "rol": request.user.groups.get().name,
            "hoy":  hoy.strftime("%Y-%m-%dT%H:%M"),
        }
        return render(request, 'asistente/frmRegistrarEntradaMaterial.html', retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})


def registrarEntradaMaterial(request):
    if request.method == "POST":
        estado = False
        try:
            with transaction.atomic():
                codigoFactura = request.POST.get('codigoFactura')
                entregadoPor = request.POST.get('entregadoPor')
                idProveedor = int(request.POST.get('proveedor'))
                recibidoPor = int(request.POST.get('recibidoPor'))
                fechaHora = request.POST.get('fechaHora', None)
                observaciones = request.POST.get('observaciones')
                userRecibe = User.objects.get(pk=recibidoPor)
                proveedor = Proveedor.objects.get(pk=idProveedor)
                entradaMaterial = EntradaMaterial(entNumeroFactura=codigoFactura, entFechaHora=fechaHora,
                                                  entUsuarioRecibe=userRecibe, entEntregadoPor=entregadoPor,
                                                  entProveedor=proveedor, entObservaciones=observaciones)
                entradaMaterial.save()
                detalleMateriales = json.loads(request.POST.get('detalle'))
                for detalle in detalleMateriales:
                    material = Material.objects.get(
                        pk=int(detalle['idMaterial']))
                    cantidad = int(detalle['cantidad'])
                    precio = int(detalle['precio'])
                    estado = detalle['estado']
                    unidadMedida = UnidadMedida.objects.get(
                        pk=int(detalle['idUnidadMedida']))
                    detalleEntradaMaterial = DetalleEntradaMaterial(detEntradaMaterial=entradaMaterial,
                                                                    detMaterial=material, detUnidadMedida=unidadMedida,
                                                                    detCantidad=cantidad, detPrecioUnitario=precio,
                                                                    detEstado=estado)
                    detalleEntradaMaterial.save()
                estado = True
                mensaje = "Se ha registrado la entrada de materiales correctamente"
        except Error as error:
            transaction.rollback()
            mensaje = f"{error}"
        retorno = {"estado": estado, "mensaje": mensaje}
        return JsonResponse(retorno)


def getElemento(request, codigo):
    elemento = devolutivoOrMaterial(codigo)

    if elemento.__class__.__name__ == "Devolutivo":
        retorno = {
            "codigo": elemento.devElemento.eleCodigo,
            "nombre": elemento.devElemento.eleNombre,
            "tipo": elemento.devElemento.eleTipo,
            "descripcion": elemento.devDescripcion
        }
    elif elemento.__class__.__name__ == "Material":
        detalleMateriales = DetalleEntradaMaterial.objects.all().filter(detMaterial=elemento)
        if len(detalleMateriales) > 0:
            cantidades = []
            for dtMaterial in detalleMateriales:
                cantidad = {
                    "unidad": dtMaterial.detUnidadMedida.uniNombre,
                    "valor": dtMaterial.detCantidad
                }
                cantidades.append(cantidad)

            for i in range(len(cantidades)):
                for j in range(i, len(cantidades)):
                    if i != j:
                        try:
                            if cantidades[i]["unidad"] == cantidades[j]["unidad"]:
                                cantidades[i]["valor"] += cantidades[j]["valor"]
                                cantidades.pop(j)
                        except:
                            ""

            retorno = {
                "codigo": elemento.matElemento.eleCodigo,
                "nombre": elemento.matElemento.eleNombre,
                "tipo": elemento.matElemento.eleTipo,
                "cantidades": cantidades
            }
        else:
            retorno = {
                "estado": False,
                "mensaje": "Material no disponible"
            }
    else:
        retorno = {
            "Error": elemento
        }

    return JsonResponse(retorno)


def devolutivoOrMaterial(codigo):
    elemento = Elemento.objects.get(eleCodigo=codigo)

    if "MAT" in codigo:
        material = Material.objects.get(matElemento=elemento)
        return material
    elif "MAQ" in codigo or "HER" in codigo or "EQU" in codigo:
        devolutivo = Devolutivo.objects.get(devElemento=elemento)
        return devolutivo
    else:
        mensaje = "No existe ese material"
        return mensaje


def getElementos(request):
    devolutivos = Devolutivo.objects.all()
    materiales = Material.objects.all()

    elementos = []
    for devolutivo in devolutivos:
        elemento = {
            "codigo": devolutivo.devElemento.eleCodigo,
            "nombre": devolutivo.devElemento.eleNombre,
            "tipo": devolutivo.devElemento.eleTipo,
            "estado": devolutivo.devElemento.eleEstado,
            "descripcion": devolutivo.devDescripcion
        }

        elementos.append(elemento)

    for material in materiales:
        material = {
            "codigo": material.matElemento.eleCodigo,
            "nombre": material.matElemento.eleNombre,
            "tipo": material.matElemento.eleTipo,
            "estado": material.matElemento.eleEstado
        }

        elementos.append(material)

    retorno = {
        "elementos": elementos
    }

    return JsonResponse(retorno)


def newSolicitud(request):

    estado = False
    mensaje = ""
    data = json.loads(request.body)
    nombre = data['nameProyect']
    fechaRequerida = datetime.strptime(data['fechaRequerida'], "%Y-%m-%dT%H:%M")
    fechaDevolver = datetime.strptime(data['fechaDevolver'], "%Y-%m-%dT%H:%M")
    estado = "Solicitada"
    ficha = Ficha.objects.get(ficCodigo=data['ficha'])
    elementos = data['elementos']

    try:
        with transaction.atomic():
            solicitud = SolicitudElemento(
                solProyecto=nombre, solFechaHoraRequerida=fechaRequerida, solFechaHoraDevolver=fechaDevolver, solEstado=estado, solFicha=ficha, solUsuario=request.user)
            solicitud.save()

            detalleCorreo = []

            for e in elementos:
                elemento = Elemento.objects.get(eleCodigo=e['codigo'])
                cantidad = e['cantidad']

                detalleCorreo.append([elemento.eleNombre, cantidad])
    
                if e['unidad'] != "":
                    unidad = UnidadMedida.objects.get(uniNombre=e['unidad'])
                    detalle = DetalleSolicitud(
                        detCantidadRequerida=cantidad, detElemento=elemento, detSolicitud=solicitud, detUnidadMedida=unidad)
                else:
                    detalle = DetalleSolicitud(
                        detCantidadRequerida=cantidad, detElemento=elemento, detSolicitud=solicitud)

                detalle.save()

            tabla = "<table class='table table-bordered text-center fw-bold' border='1'><thead><tr><th>Elemento</th><th>Cantidad</th></tr></thead><tbody>"
            
            for det in detalleCorreo:
                tabla += f"""<tr>
                                <td> {det[0]} </td>
                                <td> {det[1]} </td>
                            </tr>"""
                                
            tabla += "</tbody></table>"
            
            estado = True
            mensaje = "Solicitud Enviada"
            #generar pdf
            instructor = request.user.first_name + " " + request.user.last_name
            archivo = generarPdf(detalleCorreo,instructor)
            #Enviar correo al usuario que hizo la solicitud
            asunto = 'Registro Solicitud De Elementos Inventario CIES-NEIVA'
            mensajeEmail = f'Cordial saludo, <b>{request.user.first_name} {request.user.last_name}</b>, nos permitimos.\
                informarle que hemos recibido su solicitud en nuestro sistema de gestion de inventario \
                del Centro de la Industria, la Empresa y los Servicios CIES de la ciudad de Neiva.<br><br>\
                <b>Datos de la Solicitud</b><br>\
                <br><b>Ficha: </b> {ficha.ficCodigo}\
                <br><b>Programa: </b> {ficha.ficNombre}\
                <br><b>Proyecto: </b> {nombre}\
                <br><b>Fecha Inicial: </b> {fechaRequerida}\
                <br><b>Fecha Final: </b> {fechaDevolver}\
                <br><br><b>Relación de Elementos Solicitados</b>\
                {tabla}\
                <br>El administrador procesará su solicitud para su revición y aprovación.\
                <br><br>Lo invitamos a ingresar a nuestro sistema en la url:\
                http://gestioninventario.sena.edu.co.'
            thread = threading.Thread(
                target=enviarCorreo, args=(asunto, mensajeEmail, [request.user.email],archivo))
            thread.start()
            #Enviar correo al los administradores del sistema
            usuariosAdmin = User.objects.filter(is_staff=True).all()
            for usuario in usuariosAdmin:
                asunto = 'Registro Solicitud De Elementos Inventario CIES-NEIVA'
                mensajeEmail = f'Cordial saludo, <b>{usuario.first_name} {usuario.last_name}</b>, nos permitimos.\
                    informarle que hemos recibido la solicitud de <b>{request.user.first_name} {request.user.last_name}</b> en nuestro sistema de gestion de inventario \
                    del Centro de la Industria, la Empresa y los Servicios CIES de la ciudad de Neiva.<br><br>\
                    <b>Datos de la Solicitud</b><br>\
                    <br><b>Ficha: </b> {ficha.ficCodigo}\
                    <br><b>Programa: </b> {ficha.ficNombre}\
                    <br><b>Proyecto: </b> {nombre}\
                    <br><b>Fecha Inicial: </b> {fechaRequerida}\
                    <br><b>Fecha Final: </b> {fechaDevolver}<br>\
                    <br><br><b>Relación de Elementos Solicitados</b>\
                    {tabla}\
                    Le pedimos que procese lo mas pronto esta solicitud para su revisión y aprovación.<br>\
                    <br><br>Lo invitamos a ingresar a nuestro sistema en la url:\
                    http://gestioninventario.sena.edu.co.'
                thread = threading.Thread(
                    target=enviarCorreo, args=(asunto, mensajeEmail, [usuario.email]))
                thread.start()
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"

    retorno = {
        "estado": estado,
        "mensaje": mensaje
    }

    return JsonResponse(retorno)

def vistaVerSolicitudesIntructor(request):
    if request.user.is_authenticated:
        retorno = {"user": request.user,
                   "rol": request.user.groups.get().name,
                   'solicitudes': SolicitudElemento.objects.filter(solUsuario=request.user).all(),}
        return render(request, "instructor/verSolicitudes.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})
def vistaVerSolicitudesAprovadas(request):
    if request.user.is_authenticated:
        retorno = {"user": request.user,
                   "rol": request.user.groups.get().name,
                   'solicitudes': SolicitudElemento.objects.filter(solEstado='Aprobada').all(),}
        return render(request, "administrador/SolicitudesAprobadas.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})
def vistaVerSolicitudesPorAprobar(request):
    if request.user.is_authenticated:
        retorno = {"user": request.user,
                   "rol": request.user.groups.get().name,
                   'solicitudes': SolicitudElemento.objects.filter(solEstado='Solicitada').all(),}
        return render(request, "administrador/SolicitudesPorAprobar.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})

def getDetalleSolicitud(request,id):
    detalleDeLaSolicitud = DetalleSolicitud.objects.filter(detSolicitud=id)
    # cantidadMaterial = DetalleEntradaMaterial.objects.values(
    #         'detMaterial').annotate(cantidad=Sum('detCantidad'))
    detSolicitud = []
    for detalle in detalleDeLaSolicitud:
        if detalle.detUnidadMedida != None:
            det = {
                'idSolicitud':detalle.detSolicitud.id,
                'codigoElemento': detalle.detElemento.eleCodigo,
                'NombreElemento': detalle.detElemento.eleNombre,
                'cantidad': detalle.detCantidadRequerida,
                'unidadMedidad': detalle.detUnidadMedida.uniNombre,
            }
        else:
             det = {
                'idSolicitud':detalle.detSolicitud.id,
                'codigoElemento': detalle.detElemento.eleCodigo,
                'NombreElemento': detalle.detElemento.eleNombre,
                'cantidad': detalle.detCantidadRequerida,
                'unidadMedidad': 'Unidad'
            }
        detSolicitud.append(det)
    retorno = {"detalleSolicitud":detSolicitud}
    return JsonResponse(retorno)

def AprobarSolicitud(request,id):
    estado = False
    try:
        with transaction.atomic():
            solicitud = SolicitudElemento.objects.get(pk=id)
            solicitud.solEstado = 'Aprobada'
            solicitud.save()
            estado = True
            mensaje = "Solicitud Aprobada"
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"
    if estado :
        #Enviar correo al usuario que hizo la solicitud
        asunto = 'Solicitud De Elementos Inventario CIES-NEIVA'
        mensajeEmail = f'Cordial saludo, <b>{solicitud.solUsuario.first_name} {solicitud.solUsuario.last_name}</b>, nos permitimos.\
            informarle que hemos aprobado su solicitud en nuestro sistema de gestion de inventario \
            del Centro de la Industria, la Empresa y los Servicios CIES de la ciudad de Neiva.<br><br>\
            <b>Datos de la Solicitud</b><br>\
            <br><b>Ficha: </b> {solicitud.solFicha.ficCodigo}\
            <br><b>Programa: </b> {solicitud.solFicha.ficNombre}\
            <br><b>Proyecto: </b> {solicitud.solProyecto}\
            <br><b>Fecha Inicial: </b> {solicitud.solFechaHoraRequerida}\
            <br><b>Fecha Final: </b> {solicitud.solFechaHoraDevolver}\
            <br><br>Lo invitamos a ingresar a nuestro sistema en la url:\
            http://gestioninventario.sena.edu.co.'
        thread = threading.Thread(
            target=enviarCorreo, args=(asunto, mensajeEmail, solicitud.solUsuario.email))
        thread.start()
    retorno = {
        'estado': estado,
        'mensaje':mensaje
    }
    
    return JsonResponse(retorno)

def listarSolicitudes(request):
    if request.user.is_authenticated:
        retorno = {"user": request.user,
                   "rol": request.user.groups.get().name,
                   'solicitudes': SolicitudElemento.objects.all(),}
        if request.user.groups.get().name == "Administrador": 
            return render(request, "administrador/verSolicitudes.html", retorno)
        else:
            return render(request, "asistente/verSolicitudes.html",retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})
    
def AtenderSolicitud(request,id):
    if request.method == "POST":
        estado = False
        try:
            with transaction.atomic():
                detalleDeLaSolicitud = DetalleSolicitud.objects.filter(detSolicitud=id)
                for detalle in detalleDeLaSolicitud:
                    cantidad = int(request.POST.get(f'cant{detalle.detElemento.eleCodigo}'))
                    observacion = request.POST.get('observaciones')
                    detSolicitud = DetalleSolicitud.objects.get(pk=detalle.id)
                    salida = SalidaDetalleSolicitud(salCantidadEntregada=cantidad,salObservaciones=observacion,
                                                    salDetalleSolicitud=detSolicitud)
                    salida.save()
                solicitud = SolicitudElemento.objects.get(pk=id)
                solicitud.solEstado = 'Atendida'
                solicitud.save()
                estado=True
                mensaje='Solicitud Atendida Correctamente'
        except Error as error:
            transaction.rollback()
            mensaje = f"{error}"
        retorno = {"estado": estado, "mensaje": mensaje}
        return JsonResponse(retorno)

def vistaGestionarInventario(request): 
    if request.user.is_authenticated:
        listaElementos = Elemento.objects.all()
        entradaMateriales = DetalleEntradaMaterial.objects.values('detMaterial__matElemento') \
                    .annotate(cantidad=Sum('detCantidad'))                    
        salidaMateriales = SalidaDetalleSolicitud.objects.values('salDetalleSolicitud__detElemento') \
                .annotate(cantidad=Sum('salCantidadEntregada'))  
                
        devolucionMateriales = DevolucionElemento.objects.values('devSalida__salDetalleSolicitud__detElemento') \
            .annotate(cantidad=Sum('devCantidadDevolucion'))          
        listaInventario = []        
        for elemento in listaElementos:
            if elemento.eleTipo == "MAT":
                elementoInventario = {
                    "codigo": elemento.eleCodigo,
                    "nombre": elemento.eleNombre,
                    "entrada": 0,
                    "salida":0,
                    "saldo":0
                }
            else:
                elementoInventario = {
                    "codigo": elemento.eleCodigo,
                    "nombre": elemento.eleNombre,
                    "entrada": 1,
                    "salida":0,
                    "saldo":0
                }
                
            for entrada in entradaMateriales:
                if elemento.id == entrada['detMaterial__matElemento']:
                    elementoInventario['entrada']=entrada['cantidad']
                        
            for entrada in devolucionMateriales:
                if elemento.id == entrada['devSalida__salDetalleSolicitud__detElemento']:
                    elementoInventario['entrada'] = elementoInventario['entrada'] + entrada['cantidad']
                        
            for salida in salidaMateriales:
                if elemento.id == salida['salDetalleSolicitud__detElemento']:
                    elementoInventario['salida']=salida['cantidad']   
                        
            elementoInventario['saldo']  = int(elementoInventario['entrada']) - int(elementoInventario['salida'])
                      
            listaInventario.append(elementoInventario)                   
        if request.user.groups.filter(name='Administrador').exists():
            retorno = {"listaInventario":listaInventario}
            return render(request,"administrador/gestionarInventario.html",retorno)
        elif request.user.groups.filter(name='Asistente').exists() :
            retorno = {"listaInventario":listaInventario}
            return render(request,"asistente/gestionarInventario.html",retorno)
        else:
            retorno = {"listaInventario":listaInventario}
            return render(request,"instructor/gestionarInventario.html",retorno) 
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html",{"mensaje":mensaje})
    
def vistaReporteGrafico(request):
    if request.user.is_authenticated:
        listaElementos = Elemento.objects.all()
        salidaMateriales = SalidaDetalleSolicitud.objects.values('salDetalleSolicitud__detElemento') \
                .annotate(cantidad=Sum('salCantidadEntregada'))
                
        instructores = User.objects.all()
        cantidadSolicitudes = SalidaDetalleSolicitud.objects.values('salDetalleSolicitud__detSolicitud__solUsuario')\
            .annotate(cantidad = Count(SalidaDetalleSolicitud.id) )
                
        xElementos=[]
        yCantidadSolicitada=[]
        colores=[]
        for elemento in listaElementos:                      
            for salida in salidaMateriales:
                if elemento.id == salida['salDetalleSolicitud__detElemento']:
                    yCantidadSolicitada.append(int(salida['cantidad'])) 
                    xElementos.append(elemento.eleNombre)
                    color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                    colores.append(color)      
                    break
                
        textprops = {"fontsize":6}              
        plt.title("Elementos Solicitados")  
        plt.pie(yCantidadSolicitada,labels=xElementos,autopct="%0.1f %%",textprops=textprops, colors=colores)    
        rutaImagen = os.path.join(settings.MEDIA_ROOT+ "\\" + "grafica1.png")    
        plt.savefig(rutaImagen)  
        
        xInstructores=[]
        yCantidadSolicitudes=[]
        
        colores=[]
        for cantidad in cantidadSolicitudes:
            yCantidadSolicitudes.append(int(cantidad['cantidad']))
            for instructor in instructores:
                if cantidad['salDetalleSolicitud__detSolicitud__solUsuario']==instructor.id:
                    xInstructores.append(instructor.first_name+ " " + instructor.last_name)
                    color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                    colores.append(color) 
                    break
                
        plt.close()        
        plt.title("Solicitudes Por Instructor") 
        plt.bar(xInstructores,yCantidadSolicitudes,color=colores)  
        plt.xlabel("Instructores")
        plt.ylabel("Cantidad Solicitudes")
        rutaImagen = os.path.join(settings.MEDIA_ROOT+ "\\" + "grafica2.png")    
        plt.savefig(rutaImagen)  
            
        plt.close()
        return render(request,"administrador/reportesEstadisticos.html")  
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html",{"mensaje":mensaje})
    
def generarPdf(datos,instructor):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial','B',12)
    pdf.mostrarDatos(datos,instructor)
    pdf.output(f'media/solicitud.pdf','F')
    return "media/solicitud.pdf"

def vistaDevolucionElementos(request):
    solicitudes = SolicitudElemento.objects.filter(solEstado='Atendida')    
    salidaDetalleSolicitudes = SalidaDetalleSolicitud.objects.all()
    retorno = {"solicitudes":solicitudes,"salidaDetalleSolicitudes": salidaDetalleSolicitudes}
    return render(request,"asistente/vistaDevoluciones.html",retorno)

def obtenerDetalleSalidaElementos(request):
    if request.method == 'POST':
        try:
            estado=False
            idSolicitud = int(request.POST['idSolicitud'])
            listaDetalle = SalidaDetalleSolicitud.objects.filter(salDetalleSolicitud__detSolicitud=idSolicitud)
            
            print(listaDetalle)
            lista=[]
            for detalle in listaDetalle:
                detalleJson={
                    "idSalidaDetalleSolicitud":detalle.id,
                    "idSolicitud": detalle.salDetalleSolicitud.detSolicitud.id,
                    "idElemento": detalle.salDetalleSolicitud.detElemento.id,
                    "nombreElemento":detalle.salDetalleSolicitud.detElemento.eleNombre,
                    "codigoElemento":detalle.salDetalleSolicitud.detElemento.eleCodigo,
                    "cantidadEntregada": detalle.salCantidadEntregada,
                    "cantidadDevolucion":0
                    
                }
                lista.append(detalleJson)
            mensaje="listado de elementos de la solicitud"
            estado=True
        except Error as error:
            transaction.rollback()
            mensaje=f"{error}"
        
        retorno={"estado":estado, "mensaje":mensaje, "detalleSolicitud":lista}
        return JsonResponse(retorno)
    
def registroDevolucionElementos(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                estado=False
                observaciones = request.POST['observaciones']
                detalleElementosDevolucion = json.loads(request.POST['detalleElementosDevolucion']) 
                #se crea para enviarlo en el correo del solicitante   
                detalleDevolucionCorreo = []
                for detalle in detalleElementosDevolucion:
                    idSolicitud = int(detalle['idSolicitud'])
                    salidaDetalleSolicitud = SalidaDetalleSolicitud.objects.get(pk=int(detalle['idSalidaDetalleSolicitud']))
                    cantidadDevolucion = int(detalle['cantidadDevolucion'])
                    devolucionElemento = DevolucionElemento(devSalida=salidaDetalleSolicitud,devUsuario=request.user,
                                devCantidadDevolucion=cantidadDevolucion,devObservaciones=observaciones)
                    
                    devolucionElemento.save()
                    elemento = salidaDetalleSolicitud.salDetalleSolicitud.detElemento
                    detalleDevolucionCorreo.append([elemento.eleNombre,salidaDetalleSolicitud.salCantidadEntregada,cantidadDevolucion])
                    
                #ahora actualizar el estado de la solicitud
                solicitud = SolicitudElemento.objects.get(pk=idSolicitud)
                instructor = solicitud.solUsuario
                solicitud.solEstado="Finalizada"
                solicitud.save()
                generarPdfDevoluciones(detalleDevolucionCorreo,instructor.first_name+" "+instructor.last_name)
                #se puede enviar correo al instructor con información de lo que se le entrega
                archivo = 'media/devolucion.pdf'
                mensaje=f'Cordial saludo,<b>{instructor.first_name} {instructor.last_name}</b>, nos permitimos \
                    informarle que que se ha registrado la devolución de elementos entragados a usted \
                    para el desarrollo de actividades de formación con sus aprendices.\
                    <br><br>Se anexa documento en formato pdf como soporte de la devolución de los elementos.\
                    Muchas gracias por su compromiso en la devolución oportuna de los elementos.'
                asunto='Registro Devolución de Elementos Inventario CIES-NEIVA' 
                thread = threading.Thread(target=enviarCorreo,
                                args=(asunto,mensaje,[instructor.email],archivo) )
                thread.start()
                estado=True
                mensaje="Se ha registrado la devolución de los elementos entregados al instructor"
        except Error as error:  
            transaction.rollback()        
            mensaje=f"{error}"
        retorno={"estado":estado, "mensaje":mensaje}
        return JsonResponse(retorno)
    
def generarPdfDevoluciones(datos,instructor):
    from appGestionInventario.pdfDevoluciones import Pdf
    doc = Pdf()
    doc.add_page()
    doc.set_font("Arial","B",12)
    doc.mostrarDatos(datos,instructor)
    doc.output(f'media/devolucion.pdf', "F")
    
    
def vistaHojaVidaDevolutivo(request,id):
    devolutivo = Devolutivo.objects.get(pk=id)
    hojaVida  = HojaVidaDevolutivo.objects.filter(hojaDevolutivo=devolutivo).first()
    retorno = {'devolutivo':devolutivo,'hojaVida':hojaVida}
    return render(request, "asistente/frmRegistrarHojaVidaDevolutivo.html",retorno) 

def registrarHojaVida(request):
    if request.method == 'POST':
        try:
            estado=False
            marcaMotor = request.POST.get("txtMarcaMotor",None)
            modeloMotor = request.POST.get("txtModelo",None)
            fabricanteMotor = request.POST.get("txtFabricanteMotor",None)
            tipoCombustibe = request.POST.get("cbTipoCombustible",None)
            tipoAceiteMotor = request.POST.get("txtTipoAceiteMotor",None)
            potenciaMotor = request.POST.get("txtPotenciaMotor",None)
            rangoTrabajo = request.POST.get("txtRangoTrabajo",None)
            voltaje = request.POST.get("txtVoltaje",None)
            peso = float(request.POST.get("txtPeso",0))
            idDevolutivo = int(request.POST["idDevolutivo"])
            idHojaVida = request.POST["idHojaVida"]
            if idHojaVida:
                devolutivo = Devolutivo.objects.get(pk=idDevolutivo)
                hojaVida = HojaVidaDevolutivo.objects.get(pk=idHojaVida)
                hojaVida.hojaMarcaMotor=marcaMotor
                hojaVida.hojaModelo=modeloMotor
                hojaVida.hojaFabricante=fabricanteMotor
                hojaVida.hojaTipoCombustible=tipoCombustibe
                hojaVida.hojaTipoAceiteMotor=tipoAceiteMotor
                hojaVida.hojaPotenciaMotor=potenciaMotor
                hojaVida.hojaRangoDeTrabajo=rangoTrabajo
                hojaVida.hojaVoltaje = voltaje
                hojaVida.hojaPeso=peso
                hojaVida.save()
                mensaje="Se ha Actualizado la hoja de vida del Elemento"  
                estado=True  
            else:
                devolutivo = Devolutivo.objects.get(pk=idDevolutivo)
                hojaVida= HojaVidaDevolutivo(hojaDevolutivo=devolutivo,hojaMarcaMotor=marcaMotor,
                                            hojaModelo=modeloMotor, hojaFabricante=fabricanteMotor,
                                            hojaTipoCombustible=tipoCombustibe, hojaTipoAceiteMotor=tipoAceiteMotor,
                                            hojaPotenciaMotor=potenciaMotor, hojaRangoDeTrabajo=rangoTrabajo,
                                            hojaVoltaje = voltaje, hojaPeso=peso)
                hojaVida.save()
                mensaje="Se ha registrado la hoja de vida del Elemento"  
                estado=True         
        except Error as error: 
            mensaje=error
            
        retorno = {"estado":estado, "mensaje":mensaje,"devolutivo":devolutivo,"hojaVida":hojaVida}
        
        return render(request, "asistente/frmRegistrarHojaVidaDevolutivo.html",retorno) 


#falta hacer que funcione
def vistaGestionarMantenimientos(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Instructor').exists() \
            or request.user.groups.filter(name='Administrador').exists() :
            elementosDevolutivos = Devolutivo.objects.all()
            ubicacion = UbicacionFisica.objects.all()
            retorno = {"listaElementosDevolutivos":elementosDevolutivos,"ubicacionFisica":ubicacion}
            print(elementosDevolutivos)
            return render(request,"instructor/vistaGestionarMantenimientos.html",retorno)
        else:
            return redirect("/inicioAsistente/")
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html",{"mensaje":mensaje}) 
    
def vistaRegistrarMantenimiento(request,id):   
    devolutivo = Devolutivo.objects.get(pk=id)
    retorno = {"devolutivo":devolutivo}
    return render (request,"instructor/frmRegistrarMantenimiento.html",retorno)

def registrarMantenimiento(request):
    """_summary_
        Función que registra mantenimiento realizado
        a uno de los equipos - maquinaria con los que cuenta
        la línea de construcción para formación
    Args:
        request (_type_): Objeto request con los datos 
        necesarios para el mantenimieto como: fecha,
        instructor encargados, observaciones realizadas,
        y personal apoyo en la realización_

    Returns:
        _type_: Retorna a la vista con un objeto Json
    """
    if request.method == 'POST':
        estado=False
        try:
            idDevolutivo = int(request.POST["idDevolutivo"])
            devolutivo = Devolutivo.objects.get(pk=idDevolutivo)
            tipoMantenimiento = request.POST["cbTipoMantenimiento"]
            instructor = request.user
            realizdoPor = request.POST["txtRealizadoPor"]
            observaciones = request.POST["txtObservaciones"]
            fechaMantenimiento = request.POST["txtFechaMantenimiento"]
            mantenimiento = Mantenimento(manElemento = devolutivo.devElemento, manTipo = tipoMantenimiento, 
                                         manUsuario = instructor, manObservaciones=observaciones, 
                                         manRealizadoPor=realizdoPor, manFechaMantenimiento = fechaMantenimiento)
            mantenimiento.save()
            mensaje="Mantenimiento registrado Satisfactoriamente"
            estado=True
            
        except Error as error: 
            mensaje=error
            
        retorno = {"estado":estado, "mensaje":mensaje}
        return render (request,"instructor/frmRegistrarMantenimiento.html",retorno) 

 
def vistaMantenimientoPorEquipo(request,id):
    elemento = Elemento.objects.get(pk=id)
    devolutivo = Devolutivo.objects.filter(devElemento=elemento).first()
    listaMantenimientos = Mantenimento.objects.filter(manElemento=elemento)
    retorno={"devolutivo":devolutivo,"listaMantenimientos":listaMantenimientos}
    return render(request, 'instructor/vistaMantenimientoEquipo.html',retorno)