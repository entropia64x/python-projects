import fitz
import re
import time

#================
# CONFIGURACIÓN
#================
inicio_t = time.time()
input_pdf = "CONAMAT. Matemáticas Simplificadas. 4ed Pearson Educación (2015)TOC.pdf"
output_pdf = "CONAMAT. Matemáticas Simplicicadas_Prueba.pdf"
output_txt = "Contenido_Mate_Simp.txt"
toc_txt = "toc_Mate_Simpl.txt"
offset = 26

#================
# FUNCIONES
#================
def obtener_areas(toc):
    areas = [item for item in toc if item[0] == 1]
    areas.extend([
                [1, 'Tablas', 1629],
                [1, 'Bibliografía', 1639],
            ])
    return areas
    
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
    
def construir_bloques(areas, total_pags):
    bloques = []
     
    for i in range(len(areas)):
        nivel, titulo, inicio = areas[i]
        
        if i < len(areas) - 1:
            fin = areas[i+1][2] - 1
        else:
            fin = total_pags
        
        bloques.append((titulo, inicio, fin))
        
    return bloques

def extraer_texto(doc, inicio, fin):
    return "\n".join(doc[i].get_text("text") for i in range(inicio, fin))

def extraer_capitulos(texto):
    return re.findall(r"(Cap[ií]tulo\s+\d+)\s*(.+)", texto)

def limpiar_texto(texto, areas, capitulos):
    texto = re.sub(r"[IVXLCDM]+\s*\n", "", texto)
    texto = re.sub(r"(\w)[\-–—¬­]\s+(\w)", r"\1\2", texto)
    texto = re.sub(r"Tablas.+\n", "", texto)
    patron_capitulos = "\n|".join(re.escape(rf"{c[0]} {c[1]}") for c in capitulos)
    texto = re.sub(patron_capitulos, "", texto, flags=re.IGNORECASE)
    patron_areas = "\n|".join(re.escape(a[1]) for a in areas)
    texto = re.sub(patron_areas, "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bcontenido\n", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"⋅", "", texto)
    texto = re.sub("\n+", "\n", texto)
    texto = re.sub(r"\s+", " ", texto)
    texto = re.sub(r"(\w)[\-–—¬­](\w)", r"\1-\2", texto)
    texto = re.sub(r"(\d+)\.\s+", r"\1\n", texto)
    texto = re.sub(r" \n", " ", texto)
    texto = re.sub(r"(\D)\n", r"\1 ", texto)
    texto = re.sub(r"Solución a los ejercicios.+\n", "", texto)
    texto = re.sub(r"(.+\, \d+) (.+\, \d+\n)", r"\1\n\2", texto)
    
    return texto

def extraer_temas(texto):
      return re.findall(r"(.+)\,\s+(\d+)\n", texto)
      
def primeras_hojas(bloques):
    toc = []
    toc.append([1, bloques[0][0], bloques[0][1]])
    toc.extend([
                [2, "Prefacio", 11],
                [2, "Agradecimientos", 13],
                [2, "Acerca de los autores", 15],
                [2, "Contenido", 17],
            ])
            
    return toc, bloques[1:]
    
def encontrar_pags_cap(pdf_path, bloques, capitulos):
    caps = []
    cap_idx = 0
    num_caps = len(capitulos)
    
    X_START = 80
    Y_START = 20
    Y_END = 120
    
    for titulo, inicio, fin in bloques:
        doc = fitz.open(pdf_path)
                
        for i in range(inicio, fin):
            pag = doc[i]
            
            if cap_idx < num_caps:
                rect = pag.rect
                clip = (rect.x0 + X_START, rect.y0 + Y_START, rect.x1, rect.y0 + Y_END)
                texto = pag.get_text("text", clip=clip)
                capitulo = capitulos[cap_idx]
                
                if re.match(rf"{capitulo[0]}\n", texto, flags=re.IGNORECASE):
                    nom_cap = capitulo[0] + ": " + capitulo[1]
                    caps.append((nom_cap, i - 1))
                    cap_idx += 1
                    
                    if cap_idx >= num_caps:
                        continue
            elif re.match(r"Solución.+", titulo):
                texto = pag.get_text("text")
                soluciones = re.findall(r"capítulo\s+\d+", texto, flags=re.IGNORECASE)
                for soln in soluciones:
                    caps.append((soln, i + 1))
            else:
                break

        doc.close()
    
    caps.extend([
                ('Tablas de logaritmos', 1629),
                ('Tablas de antilogaritmos', 1631),
                ('Tablas de valores de las funciones trigonométricas', 1633),
        ])
    return caps

def construir_toc(toc, bloques, capitulos, temas, total_paginas):
    i = 0
    j = 0
    num_caps = len(capitulos)
    num_temas = len(temas)
    
    for titulo, inicio, fin in bloques:
        toc.append([1, titulo, inicio])
        
        while i < num_caps:
            cap = capitulos[i]
            nombre_cap = cap[0]
            pag_cap = int(cap[1])
            
            if pag_cap < fin:
                toc.append([2, nombre_cap, pag_cap])
                i += 1
            else:
                break
                
            fin_cap = int(capitulos[i][1]) if i < num_caps else total_paginas
            
            while j < num_temas:
                tema = temas[j]
                nombre_tema = tema[0]
                pag_tema = int(tema[1]) + offset
                if pag_cap < pag_tema < fin_cap:
                    toc.append([3, nombre_tema, pag_tema])
                    j += 1
                else:
                    break
    return toc

def establecer_toc(doc, toc, output_pdf):
    doc.set_toc(toc)
    doc.save(output_pdf)
    print(f"El nuevo archivo se guardó en {output_pdf}.")
    
def escribe_toc_txt(toc, toc_txt):
    with open(toc_txt, "w", encoding="utf-8") as f:
        for item in toc:
            f.write(f"{item}\n")

def escribe_txt(texto, output_txt):
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(texto)

#================
# EJECUCIÓN
#================

doc = fitz.open(input_pdf)
toc_viejo = doc.get_toc()
areas = obtener_areas(toc_viejo)
bloques = construir_bloques(areas, doc.page_count)
ini_ind, fin_ind = encontrar_indice(doc)
texto = extraer_texto(doc, ini_ind, fin_ind)
capitulos = extraer_capitulos(texto)
texto = limpiar_texto(texto, areas, capitulos)
escribe_txt(texto, output_txt)
temas = extraer_temas(texto)
toc, bloques = primeras_hojas(bloques)
capitulos = encontrar_pags_cap(input_pdf, bloques, capitulos)
toc = construir_toc(toc, bloques, capitulos, temas, doc.page_count)
escribe_toc_txt(toc, toc_txt)
establecer_toc(doc, toc, output_pdf)
doc.close()
fin_t = time.time()
print(fin_t - inicio_t)
