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
        foto = request.FILES.get("fileFoto", False)
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
                user.is_staff = True  # problemas cuando se es administrador
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
                target=enviarCorreo, args=(asunto, mensaje, user.email))
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


def enviarCorreo(asunto=None, mensaje=None, destinatario=None):
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
            asunto, mensaje, remitente, [destinatario])
        correo.attach_alternative(contenido, 'text/html')
        correo.send(fail_silently=True)
    except SMTPException as error:
        print(error)


def vistaGestionarElementos(request):
    if request.user.is_authenticated:
        retorno = {"devolutivos": Devolutivo.objects.all(
        ), "user": request.user, "rol": request.user.groups.get().name}
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
        datosSesion = {"user": request.user,
                       "rol": request.user.groups.get().name}
        return render(request, "asistente/solicitudes.html", datosSesion)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})


def vistaGestionarMateriales(request):
    if request.user.is_authenticated:
        cantidadMaterial = DetalleEntradaMaterial.objects.values(
            'detMaterial').annotate(cantidad=Sum('detCantidad'))
        print(cantidadMaterial)
        retorno = {"materiales": Material.objects.all(),
                   'cantidades': cantidadMaterial,
                   "user": request.user,
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

            for e in elementos:
                elemento = Elemento.objects.get(eleCodigo=e['codigo'])
                cantidad = e['cantidad']

                if e['unidad'] != "":
                    unidad = UnidadMedida.objects.get(uniNombre=e['unidad'])
                    detalle = DetalleSolicitud(
                        detCantidadRequerida=cantidad, detElemento=elemento, detSolicitud=solicitud, detUnidadMedida=unidad)
                else:
                    detalle = DetalleSolicitud(
                        detCantidadRequerida=cantidad, detElemento=elemento, detSolicitud=solicitud)

                detalle.save()

            estado = True
            mensaje = "Solicitud Enviada"

    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"

    retorno = {
        "estado": estado,
        "mensaje": mensaje
    }

    return JsonResponse(retorno)

def vistaVerSolicitudes(request):
    if request.user.is_authenticated:
        retorno = {"user": request.user,
                   "rol": request.user.groups.get().name,
                   'solicitudes': SolicitudElemento.objects.all(),}
        return render(request, "instructor/verSolicitudes.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})

def getDetalleSolicitud(request,id):
    detalleDeLaSolicitud = DetalleSolicitud.objects.filter(detSolicitud=id)
    detSolicitud = []
    for detalle in detalleDeLaSolicitud:
        if detalle.detUnidadMedida != None:
            det = {
                'codigoElemento': detalle.detElemento.eleCodigo,
                'NombreElemento': detalle.detElemento.eleNombre,
                'cantidad': detalle.detCantidadRequerida,
                'unidadMedidad': detalle.detUnidadMedida.uniNombre
            }
        else:
             det = {
                'codigoElemento': detalle.detElemento.eleCodigo,
                'NombreElemento': detalle.detElemento.eleNombre,
                'cantidad': detalle.detCantidadRequerida,
                'unidadMedidad': 'No tiene'
            }
        detSolicitud.append(det)
    retorno = {"detalleSolicitud":detSolicitud}
    return JsonResponse(retorno)