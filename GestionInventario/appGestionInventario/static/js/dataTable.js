var idioma =
{
    "sProcessing": "Procesando...",
    "sLengthMenu": "Mostrar _MENU_ registros",
    "sZeroRecords": "No se encontraron resultados",
    "sEmptyTable": "Ningún dato disponible en esta tabla",
    "sInfo": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
    "sInfoEmpty": "Mostrando registros del 0 al 0 de un total de 0 registros",
    "sInfoFiltered": "(filtrado de un total de _MAX_ registros)",
    "sInfoPostFix": "",
    "sSearch": "Buscar:",
    "sUrl": "",
    "sInfoThousands": ",",
    "sLoadingRecords": "Cargando...",
    "oPaginate": {
        "sFirst": "Primero",
        "sLast": "Último",
        "sNext": "Siguiente",
        "sPrevious": "Anterior"
    },
    "oAria": {
        "sSortAscending": ": Activar para ordenar la columna de manera ascendente",
        "sSortDescending": ": Activar para ordenar la columna de manera descendente"
    },
    "buttons": {
        "copyTitle": 'Informacion copiada',
        "copyKeys": 'Use your keyboard or menu to select the copy command',
        "copySuccess": {
            "_": '%d filas copiadas al portapapeles',
            "1": '1 fila copiada al portapapeles'
        },

        "pageLength": {
            "_": "Mostrar %d filas",
            "-1": "Mostrar Todo"
        }
    }
};

var empresa="SERVICIO NACIONAL DE APRENDIZAJE SENA";
var fecha = new Date();
var hoy = fecha.getDate()+"/"+(fecha.getMonth()+1)+"/"+fecha.getFullYear();

/**
 *
 * @param {*} tabla tabla a utilizar
 * @param {*} titulo titulo a colocar en el documento a exportar
 * @param {*} columnas número de columnas en el datatable
 */
function cargarDataTable(tabla,titulo,col){

    var columnas=[];
    for(i=0;i<col;i++){
        columnas.push(i);
    }

    if (col>6){
        orientacion = "landscape";
    }else{
        orientacion = "portrait";
    }
    tabla.dataTable({
        "paging": true,
        "destroy":true,
        "lengthChange": true,
        "searching": true,
        "ordering": true,
        "info": true,
        "autoWidth": true,
        "language": idioma,
        "lengthMenu": [[5, 20, 50, -1], [5, 20, 50, "Mostrar Todo"]],
        dom: 'Bfrtip',
        buttons: {
            dom: {
                container: {
                    tag: 'div',
                    //className: 'flexcontent'
                },
                buttonLiner: {
                    tag: null
                }
            },
            buttons: [
                {
                    extend: 'pageLength',
                    titleAttr: 'Registros a mostrar',
                    className: 'selectTable'
                },
                {
                    extend: 'pdfHtml5',
                    footer: true,
                    className: 'bg-danger',                    
                    title: empresa,
                    messageTop: titulo,
                    orientation: orientacion,
                    pageSize: 'LETTER',                  
                    exportOptions: {
                        columns: columnas
                    },
                    customize: function (doc) {
                        doc.content[1].margin = [5, 5, 5, 5],
                        doc.pageMargins = [20, 35, 20,30 ],

                        doc.styles.title = {
                            color: '#39A900',
                            fontSize: '18',
                            alignment: 'center'
                        },
                        doc.styles.message = {
                            color: '#39A900',
                            fontSize: '14',
                            alignment: 'center'
                        },

                        doc.styles['td:nth-child(2)'] = {
                            width: '100px',
                            'max-width': '150px'
                        },

                        doc.styles.tableHeader = {
                                fillColor: '#00324D',
                                color: 'white',
                                alignment: 'center',
                        },
                        doc["header"] = function() {
                            return {
                                columns: [
                                    {
                                        image: 'data:image/png;base64,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',
                                        width: 50,
                                        height: 50
                                    }
                                ],
                                margin: [40, 20,0,0]
                            }
                        },
                        doc['footer']=(function(page, pages) {
                            return {
                                columns: [
                                    {
                                        text: "Fecha: " + hoy,
                                        alignment: 'lef',
                                        color:'#39A900',
                                    },
                                    {
                                        text: "Centro de la Industria, la Empresa y los Servicios",
                                        alignment: 'center',
                                        color:'#39A900',
                                    },

                                    {
                                        alignment: 'right',
                                        color:'#39A900',
                                        text: ['página ', { text: page.toString() },  ' de ', { text: pages.toString() }]
                                    }
                                ],
                                margin: [50, 0]
                            }
                        });


                    }
                },
                {
                    extend: 'excelHtml5',                   
                    title: empresa,
                    className: 'bg-success',
                    messageTop: titulo + "       Fecha: "+hoy,                  
                    exportOptions: {
                        columns: columnas
                    },
                },
                /*{
                    extend: 'csvHtml5',                  
                    title: empresa,
                    messageTop: titulo + "       Fecha: "+hoy,                   
                    exportOptions: {
                        columns: columnas
                    }
                },
                {
                    extend: 'print',                 
                    title: empresa,
                    messageTop: titulo + "       Fecha: "+hoy,                  
                    exportOptions: {
                        columns: columnas
                    }
                },*/


            ]
        }
    });
}
