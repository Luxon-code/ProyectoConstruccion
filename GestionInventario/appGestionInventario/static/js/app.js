$(function(){
    $("#fileFoto").on("change",mostrarImagen);
    $("#cbRolMenu").change(function(){
        if($("#cbRolMenu").val()=="Instructor"){
            location.href="/inicioInstructor/";
        } 
        if($("#cbRolMenu").val()=="Administrador"){
            location.href="/inicioAdministrador/";
        }
        if($("#cbRolMenu").val()=="Asistente"){
            location.href="/inicioAsistente/";
        }
    })
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
    $("#imagenMostrar").attr("src",url)
  }
