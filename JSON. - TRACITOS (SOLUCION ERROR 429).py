import os
import json
import requests
import xml.etree.ElementTree as ET
import time
from tkinter import Tk, Button, filedialog, messagebox

def unicode_hex(kanji: str) -> str:
    """Convierte el kanji a Unicode en 5 dígitos hexadecimales, minúscula."""
    return f"{ord(kanji):05x}"

def descargar_paths(url: str):
    """Descarga el SVG desde una URL y devuelve los paths, o None si no existe."""
    try:
        r = requests.get(url)
        if r.status_code == 404:
            return None  # No existe en esta fuente
        r.raise_for_status()
        root = ET.fromstring(r.text)
        paths = [elem.attrib["d"] for elem in root.iter() if elem.tag.endswith("path") and "d" in elem.attrib]
        return paths
    except Exception as e:
        print(f"[ERROR] Al descargar SVG desde {url}: {e}")
        return None

def obtener_paths_svg(kanji: str, max_reintentos=5, backoff_inicial=2):
    """Intenta obtener los paths SVG desde múltiples fuentes alternativas."""
    unicode_kanji = unicode_hex(kanji)

    # Lista de fuentes: (nombre, URL base con {unicode})
    fuentes = [
        ("KanjiVG", f"https://raw.githubusercontent.com/KanjiVG/kanjivg/master/kanji/{unicode_kanji}.svg"),
        ("HanziVG", f"https://raw.githubusercontent.com/skishore/hanzi-vg/master/hanzi/{unicode_kanji}.svg"),
        ("KanjiVG Extended", f"https://raw.githubusercontent.com/KanjiVG/kanjivg-extended/master/kanji/{unicode_kanji}.svg")
        # Puedes agregar más fuentes aquí si lo deseas
    ]

    for fuente, url in fuentes:
        intentos = 0
        while intentos < max_reintentos:
            paths = descargar_paths(url)
            if paths is not None:
                print(f"[OK] SVG de {kanji} encontrado en {fuente}.")
                return {"paths": paths, "fuente": fuente}
            else:
                if intentos < max_reintentos - 1:
                    espera = backoff_inicial * (2 ** intentos)
                    print(f"[REINTENTO {intentos+1}] {kanji} no encontrado en {fuente}. Reintentando en {espera:.1f} seg...")
                    time.sleep(espera)
                intentos += 1

    print(f"[NO EXISTE] SVG no encontrado para {kanji} en ninguna fuente.")
    return {"paths": [], "fuente": None}

def procesar_archivos():
    archivos = filedialog.askopenfilenames(
        title="Selecciona archivos JSON de Kanjis",
        filetypes=[("Archivos JSON", "*.json")]
    )

    if not archivos:
        return

    for archivo_path in archivos:
        try:
            with open(archivo_path, "r", encoding="utf-8") as f:
                kanjis = json.load(f)

            for k in kanjis:
                if "kanji" in k:
                    resultado = obtener_paths_svg(k["kanji"])
                    k["paths"] = resultado["paths"]
                    k["fuente"] = resultado["fuente"]
                else:
                    print(f"[OMITIDO] Objeto sin clave 'kanji': {k}")

            nombre_archivo = os.path.basename(archivo_path)
            nombre_salida = nombre_archivo.replace(".json", "_paths.json")
            ruta_salida = os.path.join(os.path.dirname(archivo_path), nombre_salida)

            with open(ruta_salida, "w", encoding="utf-8") as f_out:
                json.dump(kanjis, f_out, ensure_ascii=False, indent=2)

            print(f"[OK] {ruta_salida} generado.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar {archivo_path}:\n{str(e)}")
            continue

    messagebox.showinfo("Completado", "Todos los archivos fueron procesados.")

# Interfaz gráfica con Tkinter
ventana = Tk()
ventana.title("Agregar trazos KanjiVG/HanziVG/Alternativos")
ventana.geometry("350x150")

boton = Button(ventana, text="Seleccionar archivos JSON", command=procesar_archivos)
boton.pack(pady=40)

ventana.mainloop()
