let elementos=[]
let detalleSolicitudElementos=[]
let unidadesMedida=[]
let modalDetalleSolicitud=null;
let solicitudes=[]
let idSolicitud;
$(function(){    
    if(document.getElementById('modalDetalleSolicitud')){
        modalDetalleSolicitud = new bootstrap.Modal(document.getElementById('modalDetalleSolicitud'), {
            keyboard: false
          })
    }
    //se utiliza para las peticiones ajax con jquery
    $.ajaxSetup({
        headers:{
        'X-CSRFToken':getCookie('csrftoken')
        }
    })

    $("#btnDevolucionElementos").click(function(){
        registrarDevolucionElementos();
    })

})

/**
 * Función utilizada para hacer peticiones ajax
 * necesarias en django remplaza el csrf utilizado
 * en los formulario
 * @param {*} name 
 * @returns 
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * 
 * @param {*} id 
 * @param {*} estado 
 */
function cargarSolicitudes(id,estado){
    const solicitud = {
        "id": id,
        "estado": estado
    }
    solicitudes.push(solicitud);
}
/**
 * Función que realiza una petición para obtener 
 * los elementos entregados a los instructores
 * de acuerdo a una solicitud
 * @param {*} id 
 */
function devolucionSolicitudes(id){        
    let datos = {
        "idSolicitud": id,
    };
    $.ajax({
        url: "/obtenerDetalleSalidaElementos/",       
        data: datos,
        type:'post',
        dataType:'json',
        cache:false,
        success: function(resultado){
            console.log(resultado);
            if(resultado.estado){
                detalleSolicitudElementos = resultado.detalleSolicitud;
                mostrarDetalleDevolucionElementos();
                modalDetalleSolicitud.show();
            }
            
        }
    });   
    
}


/**
 * función que muestra en la tabla de la modal
 * de los elementos a la hora de registrar
 * devoluciones
 */
function mostrarDetalleDevolucionElementos(){
    datos = "";
    detalleSolicitudElementos.forEach(detalle => {
        
        datos += "<tr>";
        datos += "<td class='text-center'>" + detalle.codigoElemento + "</td>";     
        datos += "<td>" + detalle.nombreElemento + "</td>";          
        datos += "<td class='text-center'>" + detalle.cantidadEntregada + "</td>";       
        datos += "<td> <input type='number' class='form-control was-validated' max="+detalle.cantidadEntregada+" min='0' value='0' id=ce"+detalle.idElemento+" onkeydown='return false' onpaste='return false'></td>";
        datos += "</tr>";
    });
    //agregar a la tabla con id datosTablaMateriales
    datosTablaElementos.innerHTML = datos;
}


/**
 * función que realiza petición al servidor
 * para registrar las devoluciones de elementos
 * por parte de los instructores
 */
function registrarDevolucionElementos(){
    detalleSolicitudElementos.forEach(detalle => {        
        var id="ce"+detalle.idElemento;       
        detalle.cantidadDevolucion = parseInt(document.getElementById(id).value);   
    });

    datos = {
        detalleElementosDevolucion: JSON.stringify(detalleSolicitudElementos),
        observaciones: txtObservaciones.value
    }
    console.log(detalleSolicitudElementos);
    
    $.ajax({
        url: "/registroDevolucionElementos/",       
        data: datos,
        type:'post',
        dataType:'json',
        cache:false,
        success: function(resultado){
            console.log(resultado);
            if(resultado.estado){
                Swal.fire({
                    title: 'Gestión de Solicitudes',
                    text: resultado.mensaje,
                    icon: 'success',                   
                    confirmButtonColor: '#3085d6',                  
                    confirmButtonText: 'Continuar'
                  }).then((result) => {
                    if (result.isConfirmed) {
                      location.href="/vistaDevolucionElementos/"
                    }
                  })
            }
        }
    });  
   
    
}