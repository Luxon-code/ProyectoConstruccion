from fpdf import FPDF
from datetime import datetime


class Pdf(FPDF):
    def header(self):
        # Logo
        self.image('media/logo-sena.png', 10, 8, 33)
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        self.ln()
        # Move to the right
        self.cell(60)
        # Title
        self.cell(80, 10, 'GESTIÓN INVENTARIO CIES', 0, 0, 'C')
        self.ln()
        self.cell(60)
        self.cell(80, 10, 'REPORTE DEVOLUCIÓN DE ELEMENTOS', 0, 0, 'C')
        # Line break
        self.ln(30)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')
        
        
    def mostrarDatos(self,datos,instructor):
        
        self.cell(30,10,"Instructor: ")
        self.cell(80,10,instructor)
        self.cell(30,10,"Fecha: ")
        fecha = datetime.now()
        self.cell(40,10,str(fecha.day)  + "/" +str(fecha.month) +"/"+ str(fecha.year))
        self.ln()
        #construir la tabla
        #encabezado
        self.set_font("Arial","B",12)
        self.cell(80,10,"Elemento",1,0,'C')
        self.cell(50,10,"Cantidad Entregada",1,0,'C')
        self.cell(50,10,"Cantidad Devuelta",1,0,'C')
        self.ln()
        
        #datos
        fila=110
        self.set_font("Arial","",10)
        for d in datos:
            self.cell(80,10,d[0],1,0,'L')
            self.cell(50,10,str(d[1]),1,0,'C')
            self.cell(50,10,str(d[2]),1,0,'C')
            self.ln()
            fila+=4       
        self.ln()
        self.ln()
        self.ln()      
        self.image('media/firmaInventario.png', 90, fila, 33)
        self.set_font("Arial","B",12)
        self.cell(200, 10, '_______________________________________', 0, 0, 'C')
        self.ln()
        self.cell(200, 10, 'Administrador Inventario Construcción', 0, 0, 'C')
        
    
        
        
        