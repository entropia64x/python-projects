import fitz

#================
# CONFIGURACIÓN
#================

input_pdf = "guiaocr2.pdf"
output_pdf = "guia_ocr.pdf"

#================
# EJECUCIÓN
#================

doc = fitz.open(input_pdf)

labels = []

labels.append({
    "startpage": 0,
    "style": "D",
    "prefix": "FC ",
    "firstpagenum": 1
})

labels.append({
    "startpage": 1,
    "style": "r",
    "prefix": "",
    "firstpagenum": 1
})

labels.append({
    "startpage": 7,
    "style": "D",
    "prefix": "",
    "firstpagenum": 1
})

doc.set_page_labels(labels)
doc.save(output_pdf)
doc.close()
