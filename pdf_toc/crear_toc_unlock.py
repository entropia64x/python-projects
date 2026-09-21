import re
import fitz

#================
# CONFIGURACIÓN
#================

input_txt = "texto_unlock2_modif.txt"
temas_txt = "temas_unlock2.txt"
output_txt = "texto_unlock2_limpio.txt"
input_pdf = "unlock2ocr.pdf"
output_pdf = "Unlock 2. Reading, Writing and Critical Thinking.pdf"
toc_txt = "toc_unlock2.txt"
desface = 0

#================
# FUNCIONES
#================

def encontrar_indice(doc, start=3, max_paginas=50, titulo="Contenido"):
    first = None
    last = None

    for i in range(start, max_paginas):
        text = doc[i].get_text("text")
            
        if re.search(rf"\b{titulo}\b", text, re.IGNORECASE):
            first = i
            break
    
    if first:
        for i in range(first, max_paginas):
            text = doc[i].get_text("text")
            
            if not re.search(rf"\b{titulo}\b", text, re.IGNORECASE):
                last = i
                return first, last
                    
    return first, last

def extraer_texto_de_pdf(doc, inicio, fin):
    return "\n".join(doc[i].get_text("text") for i in range(inicio, fin))

def consigue_texto_de_txt(archivo_entrada):
    with open(archivo_entrada, "r", encoding="utf-8") as f:
        return f.read()

def escribe_txt(texto, archivo_salida):
    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(texto)

def limpia_texto(texto):
    texto = re.sub(r"\n+", "\n", texto)
    texto = re.sub(r"\n ", " ", texto)
    #texto = re.sub(r"(\d+)\.", r"Unidad \1", texto)
    #texto = re.sub(r"([A-Za-zÁÉÍÓÚáéíóú\.\-\:\s]+)\n(.+\s+\d+)", r"\1 \2", texto)
    return texto

def extraer(regex, texto, sust_regex=None, sust="", drop_first=False):
    data = re.findall(regex, texto)

    if sust_regex:
        texto = re.sub(sust_regex, sust, texto)
        
    if drop_first:
        data = data[1:]
    
    return texto, data

def primeras_hojas(texto):
    toc = []
    
    toc.extend([
        [1, 'UNLOCK 2 Reading, Writing & Critical Thinking', 1],
        [2, 'CONTENTS', 3],
        [2, 'Map of the book', 4],
        [2, 'Your guide to Unlock', 8],
        ])
        
    for item in toc:
        texto = re.sub(rf"{item[1]}.+\n","", texto)
        
    return texto, toc

def crear_toc(toc, unidades, temas, total_paginas):
    i = 0
    j = 0
    num_units = len(unidades)
    num_temas = len(temas)
    
    while i < num_units:
        unidad = unidades[i]
        name = unidad[0]
        page = int(unidad[1])
        toc.append([1, name, page])
        i += 1
        page_fin = int(unidades[i][1]) if i < num_units else total_paginas
        
        while j < num_temas:
            tema = temas[j]
            nivel = int(tema[0])
            nombre = tema[1]
            pag_tema = int(tema[2])
            
            if page < pag_tema < page_fin:
                toc.append([nivel, nombre, pag_tema])
                j += 1
            else:
                break
    return toc

def escribe_toc_txt(toc, toc_txt):
    with open(toc_txt, "w", encoding="utf-8") as f:
        for item in toc:
            f.write(f"{item}\n")

def asignar_toc(input_pdf, output_pdf, toc):
    doc = fitz.open(input_pdf)
    doc.set_toc(toc)
    doc.save(output_pdf)
    print(f"El nuevo archivo se guardó en {output_pdf}.")
    doc.close()

#================
# EJECUCIÓN
#================

doc = fitz.open(input_pdf)
total_paginas = doc.page_count
ini_ind, fin_ind = encontrar_indice(doc, 2, 10, "Contents")
texto = extraer_texto_de_pdf(doc, ini_ind, fin_ind)
texto = limpia_texto(texto)
texto = consigue_texto_de_txt(input_txt)
texto, toc = primeras_hojas(texto)
texto, unidades = extraer(r"(.+)\s+(\d+)", texto)
escribe_txt(texto, output_txt)
temas_texto = consigue_texto_de_txt(temas_txt)
temas = re.findall(r"(\d)\|(.+)\|(\d+)", temas_texto)
toc = crear_toc(toc, unidades, temas, total_paginas)
escribe_toc_txt(toc, toc_txt)
asignar_toc(input_pdf, output_pdf, toc)
doc.close()
