const tiposElementos = {
    "MAT": "Material", 
    "MAQ": "Maquinaria", 
    "HER": "Herramienta",
    "EQU": "Equipo"
}

function addElement(codigo){

    if (codigo == undefined) {
        codigo = document.getElementById("inputElemento").value
    }

    url = `/elemento/${codigo}`


    fetch(url)
    .then(res => res.json())
    .then(data => {
        console.log(data)
        html = `<div class="col-sm">
        <div class="card" id="card${data.codigo}">
          <div class="card-body">
            <h4 class="card-title">${data.nombre}</h4>
            <p class="card-text">${tiposElementos[data.tipo]}</p>
            <div class="d-flex">
              <div class="input-group mb-3 w-50 me-1">
                <button class="btn btn-outline-success" type="button" id="button-addon1">+</button>
                <input type="text" class="form-control" placeholder="" aria-label="Example text with button addon"
                  aria-describedby="button-addon1">
                <button class="btn btn-outline-danger" type="button" id="button-addon1">-</button>
              </div>
              <button class="btn btn-danger mb-3 w-50">Borrar</button>
            </div>
          </div>
        </div>
      </div>`
    })
}