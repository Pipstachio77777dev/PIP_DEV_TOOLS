import os
import json
import requests
import xml.etree.ElementTree as ET
import time
import random
from tkinter import Tk, Button, filedialog, messagebox

# === CONFIGURACIÓN ===
CARPETA_CACHE = "paths_offline"
os.makedirs(CARPETA_CACHE, exist_ok=True)

PAUSA_ENTRE_KANJI = 2.5     # segundos entre kanjis
MAX_REINTENTOS = 5
BACKOFF_INICIAL = 4
BACKOFF_MAXIMO = 90
TIMEOUT_SOLICITUD = 20

# =====================

def unicode_hex(kanji: str) -> str:
    return f"{ord(kanji):05x}"

def leer_paths_local(unicode_kanji: str):
    ruta_svg = os.path.join(CARPETA_CACHE, f"{unicode_kanji}.svg")
    if not os.path.exists(ruta_svg):
        return None
    try:
        with open(ruta_svg, "r", encoding="utf-8") as f:
            root = ET.fromstring(f.read())
            paths = [elem.attrib["d"] for elem in root.iter() if elem.tag.endswith("path") and "d" in elem.attrib]
            if not paths:
                # SVG vacío o corrupto
                return None
            return paths
    except Exception as e:
        print(f"[ERROR] Al leer SVG local {ruta_svg}: {e}")
        return None

def guardar_paths_local(unicode_kanji: str, contenido_svg: str):
    ruta_svg = os.path.join(CARPETA_CACHE, f"{unicode_kanji}.svg")
    try:
        with open(ruta_svg, "w", encoding="utf-8") as f:
            f.write(contenido_svg)
    except Exception as e:
        print(f"[ERROR] No se pudo guardar SVG local {ruta_svg}: {e}")

def descargar_paths(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (KanjiCacheBot/1.0)",
        "Accept": "application/xml",
        "Cache-Control": "no-cache",
    }
    try:
        r = requests.get(url, headers=headers, timeout=TIMEOUT_SOLICITUD)
        if r.status_code == 404:
            return None, None
        if r.status_code == 429:
            retry_after = r.headers.get("Retry-After")
            espera = int(retry_after) if retry_after else random.randint(30, 90)
            print(f"[LÍMITE] GitHub devolvió 429. Esperando {espera}s antes de reintentar {url}")
            time.sleep(espera)
            return None, None
        r.raise_for_status()
        root = ET.fromstring(r.text)
        paths = [elem.attrib["d"] for elem in root.iter() if elem.tag.endswith("path") and "d" in elem.attrib]
        return paths, r.text
    except Exception as e:
        print(f"[ERROR] Al procesar SVG desde {url}: {e}")
        return None, None

def obtener_paths_svg(kanji: str):
    unicode_kanji = unicode_hex(kanji)

    # 1️⃣ Intentar cargar de caché local
    paths = leer_paths_local(unicode_kanji)
    if paths:
        print(f"[CACHE] SVG de {kanji} cargado desde caché local.")
        return {"paths": paths, "fuente": "Local"}

    # 2️⃣ Si no hay local, descargar de fuentes
    fuentes = [
        ("KanjiVG", f"https://raw.githubusercontent.com/KanjiVG/kanjivg/master/kanji/{unicode_kanji}.svg"),
        ("HanziVG", f"https://raw.githubusercontent.com/skishore/hanzi-vg/master/hanzi/{unicode_kanji}.svg"),
        ("KanjiVG Extended", f"https://raw.githubusercontent.com/KanjiVG/kanjivg-extended/master/kanji/{unicode_kanji}.svg")
    ]

    for fuente, url in fuentes:
        for intento in range(1, MAX_REINTENTOS + 1):
            paths, contenido_svg = descargar_paths(url)
            if paths:
                guardar_paths_local(unicode_kanji, contenido_svg)
                print(f"[OK] SVG de {kanji} encontrado en {fuente} (intento {intento}). Guardado localmente.")
                return {"paths": paths, "fuente": fuente}
            else:
                espera = min(BACKOFF_INICIAL * (2 ** (intento - 1)), BACKOFF_MAXIMO)
                espera_aleatoria = espera + random.uniform(0, 5)
                print(f"[ESPERA] {kanji}: intento {intento}/{MAX_REINTENTOS} fallido en {fuente}. Esperando {espera_aleatoria:.1f}s...")
                time.sleep(espera_aleatoria)

    print(f"[NO EXISTE] SVG no encontrado para {kanji} tras {MAX_REINTENTOS} intentos en todas las fuentes.")
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
                    time.sleep(PAUSA_ENTRE_KANJI)
                else:
                    print(f"[OMITIDO] Objeto sin clave 'kanji': {k}")

            nombre_salida = os.path.basename(archivo_path).replace(".json", "_paths.json")
            ruta_salida = os.path.join(os.path.dirname(archivo_path), nombre_salida)
            with open(ruta_salida, "w", encoding="utf-8") as f_out:
                json.dump(kanjis, f_out, ensure_ascii=False, indent=2)

            print(f"[OK] {ruta_salida} generado.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar {archivo_path}:\n{str(e)}")
            continue

    messagebox.showinfo("Completado", "Todos los archivos fueron procesados.")

# === Interfaz gráfica ===
ventana = Tk()
ventana.title("Agregar trazos KanjiVG/HanziVG (modo paciente con caché)")
ventana.geometry("420x160")
boton = Button(ventana, text="Seleccionar archivos JSON", command=procesar_archivos)
boton.pack(pady=40)
ventana.mainloop()
