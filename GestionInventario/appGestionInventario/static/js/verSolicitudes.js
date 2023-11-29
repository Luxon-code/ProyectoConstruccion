let detalleSolicitud = []
function verDetalleSolicitud(id){
    let url = `/detalleSolicitud/${id}`
    fetch(url)
    .then(response => response.json())
    .then(data => {
        let table = ""
        console.log(data.detalleSolicitud)
        data.detalleSolicitud.forEach((element,index)=> {
            table+= `<tr>
            <th scope="row">${index+1}</th>
            <td>${element.codigoElemento}</td>
            <td>${element.NombreElemento}</td>
            <td>${element.cantidad}</td>
            <td>${element.unidadMedidad}</td>
          </tr>`
            localStorage.idSolicitud = element.idSolicitud
        });
        tblDetalle.innerHTML = table
    })
}
function verDetalleSolicitudEntrega(id){
    let url = `/detalleSolicitud/${id}`
    fetch(url)
    .then(response => response.json())
    .then(data => {
        let table = ""
        detalleSolicitud=data.detalleSolicitud
        data.detalleSolicitud.forEach((element,index)=> {
            table+= `<tr>
            <th scope="row">${index+1}</th>
            <td>${element.codigoElemento}</td>
            <td>${element.NombreElemento}</td>
            <td>${element.cantidad}</td>
            <td>${element.unidadMedidad}</td>
            <td><input type="number" id="txtCant${element.codigoElemento}" class="form-control" value="0" min="0" max="${element.cantidad}" onkeydown="return false" onpaste="return false"></td>
          </tr>`
            localStorage.idSolicitud = element.idSolicitud
        });
        tblDetalle.innerHTML = table
    })
}

function AprobarSolicitud(){
    let id = localStorage.idSolicitud
    let url = `/aprobarSolicitud/${id}`
    fetch(url)
    .then(response => response.json())
    .then(data => {
        if(data.estado){
            Swal.fire({
                title: 'Gestion Solicitudes',
                text: data.mensaje,
                icon: 'success',
                confirmButtonColor: '#39A900',
                confirmButtonText: 'Ok'
              }).then((result) => {
                if (result.isConfirmed) {
                    location.reload()
                }
              })
        }else{
            Swal.fire('Gestion Solicitudes',data.mensaje,'error')
        }
    })
}

function atenderSolicitud(){
    let id = localStorage.idSolicitud
    let url = `/atenderSolicitud/${id}`
    var data = new FormData()
    detalleSolicitud.forEach(element => {
        data.append(`cant${element.codigoElemento}`,document.getElementById(`txtCant${element.codigoElemento}`).value)
    });
    data.append('observaciones',txtObservaciones.value)

    console.log(data)

    var options = {
        method: "POST",
        body:data,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        }
    }
    fetch(url, options)
    .then(response => response.json())
    .then((data) =>{
        if(data.estado){
            Swal.fire({
                title: 'Gestion Solicitudes',
                text: data.mensaje,
                icon: 'success',
                confirmButtonColor: '#39A900',
                confirmButtonText: 'Ok'
              }).then((result) => {
                if (result.isConfirmed) {
                    location.reload()
                }
              })
        }else{
            Swal.fire('Gestion Solicitudes',data.mensaje,'error')
        }
    })
}
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