import pypdf
import tkinter as tk
from tkinter import filedialog, messagebox
from io import BytesIO
from reportlab.pdfgen import canvas
import copy

def seleccionar_pdf_combinar():
    """
    Permite al usuario seleccionar uno o varios archivos PDF para combinar.
    """
    archivos = filedialog.askopenfilenames(
        title="Seleccionar archivos PDF",
        filetypes=[("Archivos PDF", "*.pdf")]
    )
    if archivos:
        for archivo in archivos:
            lista_archivos.insert(tk.END, archivo)

def seleccionar_membrete():
    """
    Permite al usuario seleccionar un PDF que se usará como membrete (fondo/marca de agua).
    Solo se tomará la primera página de ese PDF.
    """
    archivo = filedialog.askopenfilename(
        title="Seleccionar PDF de membrete",
        filetypes=[("Archivos PDF", "*.pdf")]
    )
    if archivo:
        # Guardamos la ruta en una variable global o de la ventana
        global pdf_membrete
        pdf_membrete = archivo
        etiqueta_membrete.config(text=f"Membrete seleccionado:\n{archivo}")

def crear_pagina_numeracion(numero, total, width, height):
    """Crea un PDF de una sola página con la numeración indicada."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(width, height))
    texto = f"Página {numero} de {total}"
    c.setFont("Helvetica", 10)
    text_width = c.stringWidth(texto, "Helvetica", 10)
    x = width - text_width - 40
    y = 20
    c.drawString(x, y, texto)
    c.save()
    buffer.seek(0)
    return buffer

def procesar_y_guardar():
    """
    Combina todos los PDFs seleccionados en la lista.
    - Si existe un PDF de membrete, se aplica como fondo a cada página resultante.
    - Luego solicita al usuario la ruta para guardar el PDF final.
    """
    archivos_pdf = lista_archivos.get(0, tk.END)
    if not archivos_pdf:
        messagebox.showwarning("Atención", "No se han seleccionado archivos para combinar.")
        return

    # Paso 1: Combinar todos los PDFs seleccionados en uno solo
    pdf_combinado = pypdf.PdfWriter()
    for ruta_pdf in archivos_pdf:
        try:
            lector = pypdf.PdfReader(ruta_pdf)
            for pagina in lector.pages:
                pdf_combinado.add_page(pagina)
        except pypdf.errors.PdfReadError:
            messagebox.showerror("Error", f"No se pudo leer el archivo PDF: {ruta_pdf}")
            return

    # Paso 2 (opcional): Aplicar membrete si se ha seleccionado uno
    #    Para ello iteramos sobre cada página combinada y la 'mergeamos' con la primera página del membrete.
    if pdf_membrete is not None:
        try:
            lector_membrete = pypdf.PdfReader(pdf_membrete)
            # Tomamos la primera página del PDF de membrete
            pagina_fondo = lector_membrete.pages[0]
            
            # Extraemos todas las páginas combinadas en un nuevo objeto,
            # para poder fusionar y reescribir correctamente:
            paginas_temporales = pdf_combinado.pages[:]
            
            # Limpiamos el PdfWriter para volver a llenarlo con las páginas ya fusionadas
            pdf_combinado = pypdf.PdfWriter()
            
            for pagina in paginas_temporales:
                # Clonamos la página para no modificar el objeto original
                pagina_clon = copy.copy(pagina)
                # Mergeamos la página de fondo en la página clonada
                pagina_clon.merge_page(pagina_fondo)
                # Agregamos la página resultante al writer
                pdf_combinado.add_page(pagina_clon)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo aplicar el membrete:\n{e}")
            return

    # Paso 3 (opcional): Agregar numeración de páginas
    if numerar_paginas_var.get():
        paginas_temporales = pdf_combinado.pages[:]
        pdf_combinado = pypdf.PdfWriter()
        total_paginas = len(paginas_temporales)
        for indice, pagina in enumerate(paginas_temporales, start=1):
            width = float(pagina.mediabox.width)
            height = float(pagina.mediabox.height)
            buffer = crear_pagina_numeracion(indice, total_paginas, width, height)
            numero = pypdf.PdfReader(buffer).pages[0]
            pagina.merge_page(numero)
            pdf_combinado.add_page(pagina)

    # Paso 4: Guardar el PDF final
    ruta_salida = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Archivos PDF", "*.pdf")],
        title="Guardar PDF combinado"
    )
    if not ruta_salida:
        # El usuario canceló la selección de archivo
        return

    try:
        with open(ruta_salida, "wb") as salida_pdf:
            pdf_combinado.write(salida_pdf)
        messagebox.showinfo("Completado", "El PDF se ha creado y guardado exitosamente.")
    except IOError:
        messagebox.showerror("Error", "No se pudo escribir en el archivo de salida.")

def limpiar_lista():
    """
    Limpia la lista de archivos seleccionados y reinicia el membrete.
    """
    lista_archivos.delete(0, tk.END)
    global pdf_membrete
    pdf_membrete = None
    etiqueta_membrete.config(text="Membrete seleccionado:\nNinguno")

# Variable global para almacenar la ruta del PDF de membrete (None si no se ha seleccionado)
pdf_membrete = None

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Combinar y Membretear PDF")
ventana.geometry("650x450")

# Variable para controlar la numeración de páginas
numerar_paginas_var = tk.BooleanVar(master=ventana, value=False)

# Etiquetas instructivas
etiqueta_instrucciones = tk.Label(
    ventana,
    text="1) Selecciona los PDFs a combinar.\n"
         "2) (Opcional) Selecciona un PDF para usar como membrete.\n"
         "3) (Opcional) Activa la numeración de páginas.\n"
         "4) Haz clic en 'Procesar y Guardar' para generar el PDF final.",
    font=("Helvetica", 11),
    justify=tk.LEFT
)
etiqueta_instrucciones.pack(pady=10)

# Botones de selección y procesamiento
frame_botones = tk.Frame(ventana)
frame_botones.pack()

boton_seleccionar_pdf = tk.Button(
    frame_botones, 
    text="Seleccionar PDFs a combinar", 
    command=seleccionar_pdf_combinar
)
boton_seleccionar_pdf.grid(row=0, column=0, padx=5, pady=5)

boton_membrete = tk.Button(
    frame_botones, 
    text="Seleccionar PDF de membrete (opcional)", 
    command=seleccionar_membrete
)
boton_membrete.grid(row=0, column=1, padx=5, pady=5)

boton_procesar = tk.Button(
    frame_botones, 
    text="Procesar y Guardar", 
    command=procesar_y_guardar
)
boton_procesar.grid(row=0, column=2, padx=5, pady=5)

check_numeracion = tk.Checkbutton(
    frame_botones,
    text="Agregar numeración",
    variable=numerar_paginas_var
)
check_numeracion.grid(row=1, column=0, columnspan=3, pady=5)

# Lista para mostrar los PDFs seleccionados
lista_archivos = tk.Listbox(ventana, selectmode=tk.MULTIPLE, width=80)
lista_archivos.pack(pady=10)

# Botón para limpiar la lista
boton_limpiar = tk.Button(ventana, text="Limpiar Lista", command=limpiar_lista)
boton_limpiar.pack(pady=5)

# Etiqueta para mostrar el PDF de membrete seleccionado
etiqueta_membrete = tk.Label(
    ventana,
    text="Membrete seleccionado:\nNinguno",
    font=("Helvetica", 10),
    justify=tk.LEFT
)
etiqueta_membrete.pack(pady=5)

# Iniciar el bucle principal de la interfaz
ventana.mainloop()
