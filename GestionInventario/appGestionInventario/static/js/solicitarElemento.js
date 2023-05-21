const tiposElementos = {
    "MAT": "Material",
    "MAQ": "Maquinaria",
    "HER": "Herramienta",
    "EQU": "Equipo"
}

function getElements() {
    url = `/elementos/`

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
            codigo ??= s.value
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

    url = `/elemento/${codigo}`

    fetch(url)
        .then(res => res.json())
        .then(data => {
            let html = `<div class="col-sm" id="card${data.codigo}">
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
                <input type="number" class="form-control" id="c${data.codigo}" value="1" min="1">
                <button class="btn btn-danger" type="button" onclick="loseCantidad('c${data.codigo}')">-</button>
              </div>
              ${data.cantidades != undefined ? cantidades(data.cantidades) : ""}
            </div>
          </div>
        </div>
      </div>`
            let card = document.getElementById(`card${data.codigo}`)
            card == undefined ? document.getElementById("detalleElementos").innerHTML += html : addCantidad(`c${data.codigo}`)
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

function cantidades(cantidades) {
    let html = `<select class="form-select w-50 mb-3" name="unidad">`
    cantidades.forEach(c => {
        html += `<option value="${c.unidad}">${c.unidad}</option>`
    });
    html += `</select>`
    return html
}

function deleteCard(codigo) {
    document.getElementById(codigo).remove()
}

getElements()