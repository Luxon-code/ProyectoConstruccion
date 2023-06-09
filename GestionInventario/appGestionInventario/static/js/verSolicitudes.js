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
        });
        tblDetalle.innerHTML = table
    })
}