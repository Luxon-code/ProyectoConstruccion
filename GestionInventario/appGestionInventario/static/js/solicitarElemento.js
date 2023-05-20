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
                        <p class="card-text">${elemento.descripcion != undefined ? elemento.descripcion : ""}</p>
                        </div>
                        <button class="btn btn-primary" onclick="addElement('${elemento.codigo}')">Add</button>
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
            s.value != "" ? codigo = s.value : ""
            s.value = ""
        });
    }

    if (codigo == undefined){
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
          <div class="card-body">
            <h4 class="card-title">${data.nombre}</h4>
            <p class="card-text">${tiposElementos[data.tipo]}</p>
            ${data.cantidades == undefined ? "" : unidades(data.cantidades)}
            <div class="d-flex">
              <div class="input-group mb-3 w-50 me-1">
                <button class="btn btn-success" type="button" id="button-add" onclick="addCantidad('c${data.codigo}')">+</button>
                <input type="number" class="form-control" id="c${data.codigo}" value="1" min="1">
                <button class="btn btn-danger" type="button" onclick="loseCantidad('c${data.codigo}')">-</button>
              </div>
              <button class="btn btn-danger mb-3 w-50">Borrar</button>
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
    document.getElementById(codigo).value >= 1 ? document.getElementById(codigo).value++ : document.getElementById(codigo).value = 1
}

function loseCantidad(codigo) {
    document.getElementById(codigo).value > 1 ? document.getElementById(codigo).value-- : document.getElementById(codigo).value = 1
}

function unidades(cantidades) {
    console.log(cantidades)
    let html = ""
    cantidades.forEach(c => {
        html += `<p class="card-text">${c.valor + c.unidad}</p>`
    });
    return html
}

getElements()