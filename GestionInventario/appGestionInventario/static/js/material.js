let materiales = []
let entradaMateriales = []
let unidadesMedidas = []
const csrftoken = getCookie('csrftoken')
$(function () {
    $('#btnAgregarMaterialDetalle').click(function () {
        agregarMaterialAlDetalle()
    })
    $('#btnRegistrarDetalle').click(function () {
        registrarDetalleEntrada()
    })
})

function registrarDetalleEntrada(){
    data = {
        "codigoFactura": $('#txtFactura').val(),
        "entregadoPor": $('#txtEntregadoPor').val(),
        "proveedor": $('#cbProveedor').val(),
        "recibidoPor": $('#cbRecibidoPor').val(),
        "observaciones": $('#txtObservaciones').val(),
        "fechaHora": $('#txtFecha').val(),
        "detalle": JSON.stringify(entradaMateriales),
    }
    var options = {
        method: "POST",
        mode: "same-origin",
        body:data,
        headers: {
            'X-CSRFToken': csrftoken,
        }
    }
    fetch("/registrarEntradaMaterial/",options)
    .then(response => response.json())
    .then((data)=>{
        console.log(data)
    })
    .catch((error)=>{
        console.log("Error al registrar Entrada Material.")
    })
}
/**
 * Agrega cada material al arreglo entradaMateriales,
 * valida que el mismo material no se haya agreado dos veces
 */
function agregarMaterialAlDetalle(){
    //averiguar si se ha agregado el material
    const m = entradaMateriales.find(material=>material.idMaterial == $('#cbMaterial').val())
    if(m==null){
        const material = {
            "idMaterial": $('#cbMaterial').val(),
            "cantidad": $('#txtCantidad').val(),
            "precio": $('#txtPrecio').val(),
            "idUnidadMedida": $('#cbUnidadMedida').val(),
            "estado": $('#cbEstado').val(),
        }
        entradaMateriales.push(material)
        frmEntradaMaterial.reset()
        mostrarDatosTabla()
    }else{
        Swal.fire('Entrada Materiales','El material seleccionado ya se ha agregado en el detalle. Verifique','info')
    }
}
/**
 * muestra los materiales del arreglo entrada materiales
 * en el html en una tabla
 */
function mostrarDatosTabla(){
    datos = ""
    entradaMateriales.forEach(entrada => {
        //obtener la posicion del material en el arreglo materiales de acuerdo
        //al idMaterial del arreglo entradaMateriales ,para poder obtener el codigo
        //y nombre del material
        posM = materiales.find(material => material.idMaterial == entrada.idMaterial)
        //obtener la posicion de la unidad de medida en el arreglo unidadesMedidas de
        //acuerdo al idUnidadMedida en el arreglo entradaMateriales para poder obtner el nombre
        posU = unidadesMedidas.find(unidad=> unidad.id == entrada.idUnidadMedida)

        datos += `<tr>
        <td class="text-center">${posM.codigo}</td>
        <td>${posM.nombre}</td>
        <td class="text-center">${entrada.cantidad}</td>
        <td class="text-end">$ ${entrada.precio}.00</td>
        <td>${posU.nombre}</td>
        <td class="text-center">${entrada.estado}</td>
        </tr>`
    });
    datosTablaMateriales.innerHTML = datos
}
/**
 * recibe los materiales en la vista y los guarda en el arreglo
 * @param {*} idMaterial 
 * @param {*} codigo 
 * @param {*} nombre 
 */
function cargarMateriales(idMaterial,codigo,nombre){
    const material = {
        "idMaterial": idMaterial,
        "codigo": codigo,
        "nombre": nombre,
    }
    materiales.push(material)
}
/**
 * recibe la unidades de medida en la vista
 * y los guarda en el arreglo
 * @param {*} id 
 * @param {*} nombre 
 */
function cargarUnidadesMedida(id,nombre){
    const unidadMedida ={
        "id": id,
        "nombre": nombre,
    }
    unidadesMedidas.push(unidadMedida)
}
/**
 * función necesaria para hecer peticiones
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