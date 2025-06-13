# PDF_UNION
Une PDFs, inserta un membrete y permite numerar las páginas del documento

## Instalación

1. Crea un entorno virtual:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Requisitos

- Python 3.8 o superior.
- Tener Tkinter disponible. En sistemas Linux suele instalarse con el paquete
  `python3-tk`.
- Ejecutar el programa en un entorno con pantalla, ya que se usa una interfaz
  gráfica.

## Uso

Tras instalar las dependencias, ejecuta el script de la siguiente forma:

```bash
python combinar_pdf_2.py
```

Al abrirse, se mostrará una ventana que permite:

- Elegir los PDFs a combinar.
- Seleccionar un PDF opcional como membrete (se usará su primera página).
- Activar o no la numeración de páginas.
- Limpiar la lista de archivos cargados y finalmente procesar y guardar el
  resultado combinado.

La aplicación emplea PyPDF y ReportLab para fusionar y numerar los documentos.
