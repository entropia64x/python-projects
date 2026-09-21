import fitz  # PyMuPDF
import ast

def leer_toc_desde_txt(ruta_txt):
    toc = []

    with open(ruta_txt, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()

            if not linea:
                continue  # saltar líneas vacías

            try:
                # Convierte el texto "[1, 'Título', 5]" a lista real
                entrada = ast.literal_eval(linea)

                # Validación básica
                if (
                    isinstance(entrada, list)
                    and len(entrada) == 3
                    and isinstance(entrada[0], int)
                    and isinstance(entrada[1], str)
                    and isinstance(entrada[2], int)
                ):
                    toc.append(entrada)
                else:
                    print(f"Línea inválida: {linea}")

            except Exception as e:
                print(f"Error al procesar línea: {linea}")
                print(e)

    return toc


def asignar_toc_a_pdf(pdf_entrada, pdf_salida, toc):
    doc = fitz.open(pdf_entrada)

    # Asignar tabla de contenido
    doc.set_toc(toc)

    doc.save(pdf_salida)
    doc.close()


# --- USO ---

ruta_txt = "toc_Mate_Simpl_modificado.txt"
pdf_entrada = "CONAMAT. Matemáticas Simplificadas. 4ed Pearson Educación (2015)TOC.pdf"
pdf_salida = "CONAMAT. Matemáticas Simplificadas. 4ed Pearson Educación (2015).pdf"

toc = leer_toc_desde_txt(ruta_txt)
asignar_toc_a_pdf(pdf_entrada, pdf_salida, toc)

print("TOC asignado correctamente.")
