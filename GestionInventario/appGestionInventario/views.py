from django.shortcuts import render,redirect
from appGestionInventario.models import *
from django.contrib.auth.models import Group
# Create your views here.
datosSesion={"user":None,"rutaFoto":None, "rol":None}

def inicio(request):
    return render(request,"inicio.html")

def inicioAdministrador(request):
    if request.user.is_authenticated:
        return render(request,"administrador/inicio.html", datosSesion)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html",{"mensaje":mensaje})
    
def vistaRegistrarUsuario(request):
    roles = Group.objects.all()
    retorno = {"roles":roles,"user":None}
    return render(request, "administrador/frmRegistrarUsuario.html",retorno)