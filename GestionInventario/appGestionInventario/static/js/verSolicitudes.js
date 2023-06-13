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
        console.log(data.detalleSolicitud)
        data.detalleSolicitud.forEach((element,index)=> {
            table+= `<tr>
            <th scope="row">${index+1}</th>
            <td>${element.codigoElemento}</td>
            <td>${element.NombreElemento}</td>
            <td>${element.cantidad}</td>
            <td>${element.unidadMedidad}</td>
            <td><input type="number" id="txtCant${element.NombreElemento}" class="form-control" value="0" min="0" max="${element.cantidad}"></td>
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