"""
URL configuration for GestionInventario project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from appGestionInventario import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('inicioAdministrador/',views.inicioAdministrador),
    path('inicioAsistente/',views.asistenteInicio),
    path('inicioInstructor/',views.inicioInstructor),
    path('vistaRegistrarUsuario/',views.vistaRegistrarUsuario),
    path('registrarUsuario/',views.registrarUsuario),
    path('vistaGestionarUsuarios/',views.vistaGestionarUsuarios),
    path('cambiarEstadoUsuario/<int:id>',views.cambiarEstadoUsuario),
    path('vistaGestionarCuenta/',views.vistaGestionarCuenta),
    path('modificarUsuario/<int:id>',views.modificarDatosUserPerfil),
    path('',views.vistaLogin),
    path('login/',views.login),
    path('salir/',views.salir),
    path('solicitarElementos/',views.SolicitarElementos),
    path('vistaGestionarElementos/',views.vistaGestionarElementos),
    path('hojaVidaDevolutivo/<int:id>/',views.vistaHojaVidaDevolutivo),
    path('vistaRegistrarElementos/',views.vistaRegistrarElementos),
    path('registrarElemento/',views.registrarElementos),
    path('vistaSolicitudes/',views.asistenteSolicitudes),
    path('vistaGestionarMateriales/',views.vistaGestionarMateriales),
    path('vistaRegistrarMateriales/',views.vistaRegistrarMateriales),
    path('registrarMaterial/',views.registrarMaterial),
    path('vistaRegistrarEntradaMaterial/',views.vistaRegistrarEntradaMaterial),
    path('registrarEntradaMaterial/',views.registrarEntradaMaterial),
    path('elemento/<str:codigo>', views.getElemento),
    path('elementos/', views.getElementos),
    path('newSolicitud/', views.newSolicitud),
    path('registrarHojaVida/', views.registrarHojaVida),
    path('vistaVerSolicitudes/',views.vistaVerSolicitudesIntructor),
    path('detalleSolicitud/<int:id>',views.getDetalleSolicitud),
    path('verSolicitudesAprobadas/',views.vistaVerSolicitudesAprovadas),
    path('verSolicitudesPorAprobar/',views.vistaVerSolicitudesPorAprobar),
    path('aprobarSolicitud/<int:id>',views.AprobarSolicitud),
    path('verSolicitudes/',views.listarSolicitudes),
    path('vistaGestionarMantenimientos/',views.vistaGestionarMantenimientos),
    path('vistaRegistrarMantenimiento/<int:id>',views.vistaRegistrarMantenimiento),
    path('vistaMantenimientoEquipo/<int:id>',views.vistaMantenimientoPorEquipo),
    path('registrarMantenimiento/',views.registrarMantenimiento),
    path('vistaDevolucionElementos/',views.vistaDevolucionElementos),
    path('atenderSolicitud/<int:id>',views.AtenderSolicitud),
    path('vistaGestionarInventario/',views.vistaGestionarInventario),
    path('resportesEstadisticos/',views.vistaReporteGrafico),
    path('obtenerDetalleSalidaElementos/',views.obtenerDetalleSalidaElementos),
    path('registroDevolucionElementos/',views.registroDevolucionElementos),
    path("reset_password/",auth_views.PasswordResetView.as_view(template_name="recuperarPassword/PasswordResetView.html"),name="password_reset"),
    path("reset_password_send/",auth_views.PasswordResetDoneView.as_view(template_name="recuperarPassword/PasswordResetDoneView.html"),name="password_reset_done"),
    path("reset/<uidb64>/<token>/",auth_views.PasswordResetConfirmView.as_view(template_name="recuperarPassword/PasswordResetConfirmView.html"),name="password_reset_confirm"),
    path("reset_password_complete/",auth_views.PasswordResetCompleteView.as_view(template_name="recuperarPassword/PasswordResetCompleteView.html"),name="password_reset_complete"),
]

if settings.DEBUG:
    urlpatterns += static (settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
