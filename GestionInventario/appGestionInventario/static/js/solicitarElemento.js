function addElement(codigo){

    if (codigo == undefined) {
        codigo = document.getElementById("inputElemento").value
    }

    url = `/elemento/${codigo}`


    fetch(url)
    .then(res => res.json())
    .then(data => {
        console.log(data)
    })
}