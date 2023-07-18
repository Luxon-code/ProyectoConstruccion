from fpdf import FPDF
from datetime import datetime
class PDF(FPDF):
    def header(self):
        # Logo
        self.image('media/logo-sena.png', 10, 8, 33)
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 10, 'GESTION INVENTARIO CIES',align='C')
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
    def mostrarDatos(self,datos,intructor):
        self.set_font('Arial', 'B',10)
        self.cell(20,10,"Instructor: ")
        self.cell(80,10,intructor)
        self.cell(20,10,"Fecha: ")
        fecha = datetime.now().strftime("%Y-%m-%d")
        self.cell(80,10,fecha)
        self.ln()
        
        #construir tabla
        #encabezado
        self.set_font('Arial', 'B',12)
        self.set_fill_color(57, 169, 0)
        self.set_text_color(255,255,255)
        self.cell(80,10,"Elemento",border=1,align='C',fill=True)
        self.cell(30,10,"Cantidad",border=1,align='C',fill=True)
        self.ln()
        
        self.set_font('Arial',"",12)
        self.set_text_color(0,0,0)
        for dato in datos:
            self.cell(80,10,dato[0],border=1,align='C')
            self.cell(30,10,str(dato[1]),border=1,align='C')
            self.ln()
        