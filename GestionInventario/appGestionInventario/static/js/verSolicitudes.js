function verDetalleSolicitud(id){
    let url = `/detalleSolicitud/${id}`
    fetch(url)
    .then(response => response.json())
    .then(data => {
        console.log(data)
    })
}