$(function(){
    $("#fileFot").on("change",mostrarImagen);
})
/**
 * A partir de la selección de una 
 * imagen en el control fileFoto del
 * formulario, se obtiene la url para
 * poder mostrarlo en un control tipo
 * IMG
 * @param {*} evento 
 */
function mostrarImagen(evento){
    const archivos = evento.target.files
    const archivo = archivos[0]
    const url = URL.createObjectURL(archivo)  
    $("#imagenMostra").attr("src",url)
  }
