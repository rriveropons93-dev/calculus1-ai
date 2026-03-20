import pdfplumber
import os

def cargar_pdfs(carpeta="pdfs"):
    texto_total = ""
    archivos = [f for f in os.listdir(carpeta) if f.endswith(".pdf")]
    for archivo in archivos:
        try:
            with pdfplumber.open(os.path.join(carpeta, archivo)) as pdf:
                for pagina in pdf.pages:
                    texto = pagina.extract_text()
                    if texto:
                        texto_total += texto + "\n"
        except Exception as e:
            print(f"Reading Error {archivo}: {e}")
    return texto_total
