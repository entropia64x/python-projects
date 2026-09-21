import re
import fitz

#================
# CONFIGURACIÓN
#================

input_txt = "toc_guia.txt"
temas_txt = "temas_unlock2.txt"
output_txt = "texto_limpio.txt"
input_pdf = "guia_ocr.pdf"
output_pdf = "Guía CONAMAT TOC2.pdf"
toc_txt = "toc_guia_final.txt"

desface = 7
total_paginas = 561

#================
# FUNCIONES
#================

def consigue_texto(archivo_entrada):
    with open(archivo_entrada, "r", encoding="utf-8") as f:
        return f.read()

def escribe_txt(texto, archivo_salida):
    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(texto)

def limpia_texto(texto):
    texto = re.sub(r"\n+", "\n", texto)
    texto = re.sub(r"\n ", " ", texto)
    texto = re.sub(r"(\d+)\.", r"Unidad \1", texto)
    texto = re.sub(r"([A-Za-zÁÉÍÓÚáéíóú\.\-\:\s]+)\n(.+\s+\d+)", r"\1 \2", texto)
    return texto

def extraer(regex, texto, sust_regex=None, sust="", drop_first=False):
    data = re.findall(regex, texto)

    if sust_regex:
        texto = re.sub(sust_regex, sust, texto)
        
    if drop_first:
        data = data[1:]
    
    return texto, data

def extraer_temas_con_subtemas(texto, subtemas_texto):
    subtemas = re.findall(r"(.+)\s+(\d+)\n", subtemas_texto)
    temas_y_subtemas = []
    vector_texto = texto.split("\n")
    
    patron_subtemas = "|".join(re.escape(n[0]) for n in subtemas)
    texto = re.sub(patron_subtemas,"", texto)
    
    i = 0
    
    while i < len(vector_texto) - 1:
        tema = re.match(r"(.+)\s+(\d+)", vector_texto[i])
        temas_y_subtemas.append((tema.group(1), tema.group(2), 0, 0))
        j = i + 1
        
        while subtemas:
            match = re.match(r"(.+)\s+\d+$", vector_texto[j])
            s = subtemas[0]

            if match.group(1) == s[0]:
                temas_y_subtemas.append((tema.group(1), tema.group(2), s[0], s[1]))
                del subtemas[0]
                j += 1
            else:
                i = j
                break
        
        if not subtemas:
            i += 1

    return texto, temas_y_subtemas

def primeras_hojas(texto):
    toc = []
    
    toc.extend([
        [1, 'Guía de estudio para ingresar al bachillerato', 1],
        [2, '¿Qué es?', 4],
        [2, 'Prefacio', 5],
        [2, 'Contenido', 6],
        ])
        
    for item in toc:
        texto = re.sub(rf"{item[1]}\s+\d+\n","", texto)
        
    return texto, toc

def crear_toc(texto, toc, secciones, contenidos, unidades, respuestas, temas_y_subtemas):
    contador = 1
    
    while secciones:
        s = secciones[0]
        c = contenidos[0]
        pag_sec = int(s[1]) + desface
        pag_cont = int(c[1]) + desface
        toc.append([1, s[0], pag_sec])
        toc.append([2, c[0], pag_cont])
        
        try:
            pag_sec_fin = int(secciones[1][1]) + desface
        except:
            pag_sec_fin = total_paginas
        
        del secciones[0]
        del contenidos[0]
        contador += 1

        while unidades:
            u = unidades[0]
            unidad = f"Unidad {u[0]}: {u[1]}"
            pag_unid = int(u[2]) + desface
            
            try:
                pag_unid_fin = int(unidades[1][2]) + desface
            except:
                pag_unid_fin = total_paginas
            
            if pag_cont < pag_unid < pag_sec_fin:
                toc.append([2, unidad, pag_unid])
                del unidades[0]
            else:
                r = respuestas[0]
                toc.append([2, r[0], int(r[1]) + desface])
                del respuestas[0]
                break
            
            while temas_y_subtemas:
                t_con_s = temas_y_subtemas[0]
                tema = t_con_s[0]
                pag_tema = int(t_con_s[1]) + desface
                sub = t_con_s[2]
                pag_sub = int(t_con_s[3]) + desface
                
                if pag_unid <= pag_tema < pag_unid_fin:
                    if not sub:
                        if contador > 5 and re.match(r"Ejercicios.*", tema):
                            toc.append([2, tema, pag_tema])
                        else:
                            toc.append([3, tema, pag_tema])
                    else:
                        toc.append([4, sub, pag_sub])
                    del temas_y_subtemas[0]
                else:
                    break

    return texto, toc

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

texto = consigue_texto(input_txt)
texto = limpia_texto(texto)
texto, unidades = extraer(r"Unidad\s*(\d+)(.+)\s+(\d+)", texto, r"\nUnidad\s*\d+.+", "")
texto, secciones = extraer(r"(.+)\s(\d+)\nContenido", texto, r"\n.+\s\d+(\nContenido)", r"\1", True)
texto, contenidos = extraer(r"(Contenido.*)\s+(\d+)", texto, r"\nContenido.*", "", True)
texto, respuestas = extraer(r"(Respuestas a.+)\s(\d+)", texto, r"\nRespuestas a.+")
subtemas_texto = consigue_texto(subtemas_txt)
subtemas_texto = limpia_texto(subtemas_texto)
texto, toc = primeras_hojas(texto)
texto, temas_y_subtemas = extraer_temas_con_subtemas(texto, subtemas_texto)
texto, toc = crear_toc(texto, toc, secciones, contenidos, unidades, respuestas, temas_y_subtemas)
escribe_txt(texto, output_txt)
escribe_toc_txt(toc, toc_txt)
asignar_toc(input_pdf, output_pdf, toc)
