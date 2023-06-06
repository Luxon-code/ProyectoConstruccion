const tiposElementos = {
    "MAT": "Material",
    "MAQ": "Maquinaria",
    "HER": "Herramienta",
    "EQU": "Equipo"
}

function getElements() {
    let url = `/elementos/`

    fetch(url)
        .then(res => res.json())
        .then(data => {
            let html = ""
            let datalist = ""
            data.elementos.forEach(elemento => {
                html += `<div class="card my-1">
                        <div class="card-body d-flex align-items-center justify-content-between">
                        <div>
                        <p class="card-text">${elemento.nombre}</p>
                        <p class="card-text">${elemento.descripcion ??= ""}</p>
                        </div>
                        <button class="btn btn-primary" onclick="addElement('${elemento.codigo}')" data-bs-dismiss="offcanvas">Add</button>
                        </div>
                        </div>`
                datalist += `<option value="${elemento.codigo}">${elemento.nombre}</option>`
            });
            document.getElementById("offcanvasElements").innerHTML = html
            document.getElementById("elementos").innerHTML = datalist
        })
}

function addElement(codigo) {

    if (codigo == undefined) {
        search = document.getElementsByName("search")
        search.forEach(s => {
            codigo ||= s.value //! operador assignment
            s.value = ""
        });
    }

    if (codigo == undefined) {
        Swal.fire(
            'Campo Vacio',
            'Se necesita el elemento del codigo',
            'warning'
        )
        return true
    }

    let url = `/elemento/${codigo}`

    fetch(url)
        .then(res => res.json())
        .then(data => {
            if (data.estado == false) {
                Swal.fire(
                    'Material No Disponible',
                    'No hay nada de este material, sorry :c',
                    'error'
                )
                return ""
            }

            let html = `<div class="col-sm" id="card${data.codigo}" name="elemento">
                        <div class="card">
                            <div class="card-header d-flex justify-content-between">
                                <h4 class="card-title">${data.nombre}</h4>
                                <button type="button" class="btn-close" onclick="deleteCard('card${data.codigo}')"></button>
                            </div>
                            <div class="card-body">
                            <p class="card-text">${tiposElementos[data.tipo]}</p>
                            <div class="d-flex justify-content-center">
                            <div class="input-group mb-3 ${data.cantidades != undefined ? "w-50" : "w-75"} me-1">
                                <button class="btn btn-success" type="button" id="button-add" onclick="addCantidad('c${data.codigo}')">+</button>
                                <input type="number" class="form-control" id="c${data.codigo}" value="1" min="1" name="cantidad">
                                <button class="btn btn-danger" type="button" onclick="loseCantidad('c${data.codigo}')">-</button>
                            </div>
                            ${data.cantidades != undefined ? cantidades(data.cantidades, data.codigo) : ""}
                            </div>
                        </div>
                        </div>
                    </div>`
            let card = document.getElementById(`card${data.codigo}`)
            card == undefined ? document.getElementById("detalleElementos").innerHTML += html : addCantidad(`c${data.codigo}`)
            checkCantidades(`c${data.codigo}`)
        })
        .catch(err => {
            Swal.fire(
                'Codigo Erroneo',
                'No existe ningun elemento con ese codigo',
                'error'
            )
        })
}

function addCantidad(codigo) {
    let cantidad = document.getElementById(codigo)
    cantidad.value >= 1 ? cantidad.value++ : cantidad.value = 1
}

function loseCantidad(codigo) {
    let cantidad = document.getElementById(codigo)
    cantidad.value > 1 ? cantidad.value-- : cantidad.value = 1
}

function cantidades(cantidades, codigo) {
    let html = `<select class="form-select w-50 mb-3" name="unidad" id="u${codigo}">`
    cantidades.forEach(c => {
        html += `<option value="${c.unidad}">${c.unidad}</option>`
    });
    html += `</select>`
    return html
}

function deleteCard(codigo) {
    document.getElementById(codigo).remove()
}

function deleteAllElements() {
    document.getElementById("detalleElementos").innerHTML = ""
}

function prepararSolicitud() {
    let detalle = document.getElementById("detalleElementos")
    myModal = new bootstrap.Modal(document.getElementById('solicitudModal'))
    if (detalle.innerHTML == "") {
        Swal.fire(
            'Solicitud Vacia',
            'Debe haber un elemento minimo',
            'warning'
        )
        return
    }
    myModal.toggle()
}

function enviarSolicitud() {
    let nameProyect = document.getElementById("nameProyect").value
    let ficha = document.getElementById("ficha").value
    let fechaR = document.getElementById("dateProyectRequerida").value
    let fechaD = document.getElementById("dateProyectDevolver").value
    let cardElementos = document.getElementsByName("elemento")

    let elementos = []

    cardElementos.forEach(cardElement => {
        let codigo = cardElement.id.slice(4)
        let cantidad = document.getElementById(`c${codigo}`).value
        let unidad = document.getElementById(`u${codigo}`)
        let elemento = {
            "codigo": codigo,
            "cantidad": parseInt(cantidad),
            "unidad": unidad == null ? "" : unidad.value
        }
        elementos.push(elemento)
    })

    if (nameProyect == "") {
        Swal.fire(
            'Nombre Del Proyecto',
            'El campo esta vacio',
            'warning'
        )
        return
    }

    let data = {
        "nameProyect": nameProyect,
        "ficha": parseInt(ficha),
        "fechaRequerida": fechaR,
        "fechaDevolver": fechaD,
        "elementos": elementos
    }

    let url = "/newSolicitud/"
    let options = {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            "Content-Type": "application/json"
        }
    }

    fetch(url, options)
        .then(res => res.json())
        .then(data => {
            if (data.estado) {
                document.getElementById("detalleElementos").innerHTML = ""
                myModal.toggle()
                Swal.fire(
                    'Solicitud Enviada',
                    data.mensaje,
                    'success'
                )
            } else {
                Swal.fire(
                    'Error',
                    data.mensaje,
                    'error'
                )
            }
        })
}

function checkCantidades(codigo) {
    let cantidad = document.getElementById(codigo)
    cantidad.addEventListener("blur", () => {
        cantidad.value <= 0 ? cantidad.value = 1 : ""
    })
}

function getCookie(name) {
    let cookieValue = null
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';')
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim()
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                return cookieValue;
            }
        }
    }
}

getElements()