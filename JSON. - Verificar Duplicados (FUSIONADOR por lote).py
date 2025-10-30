import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
from collections import defaultdict

archivo_actual = None  # Ruta del archivo actualmente cargado
datos_json = []        # Datos del JSON cargado

def cargar_json():
    global datos_json, archivo_actual
    archivo = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if not archivo:
        return

    archivo_actual = archivo

    with open(archivo, 'r', encoding='utf-8') as f:
        datos_json = json.load(f)

    duplicados = detectar_duplicados(datos_json)
    mostrar_duplicados(duplicados)

def detectar_duplicados(data):
    mapa_kanji = defaultdict(list)
    for item in data:
        kanji = item.get("kanji", "")
        mapa_kanji[kanji].append(item)
    return {k: v for k, v in mapa_kanji.items() if len(v) > 1}

def mostrar_duplicados(duplicados):
    text_area.delete(1.0, tk.END)
    if not duplicados:
        text_area.insert(tk.END, "No hay duplicados.\n")
        return
    for kanji, entradas in duplicados.items():
        text_area.insert(tk.END, f"🔁 Kanji duplicado: {kanji}\n")
        for i, item in enumerate(entradas):
            text_area.insert(tk.END, f"  Entrada {i+1}: {json.dumps(item, ensure_ascii=False)}\n")
        text_area.insert(tk.END, "\n")

def fusionar_y_guardar():
    global datos_json, archivo_actual
    if not datos_json:
        messagebox.showwarning("Aviso", "Primero debes cargar un archivo JSON.")
        return
    if not archivo_actual:
        messagebox.showerror("Error", "Ruta del archivo no disponible.")
        return

    fusionados = {}
    for item in datos_json:
        kanji = item.get("kanji", "")
        if kanji not in fusionados:
            fusionados[kanji] = item
        else:
            fusionados[kanji] = fusionar_diccionarios(fusionados[kanji], item)

    datos_json = list(fusionados.values())

    try:
        with open(archivo_actual, 'w', encoding='utf-8') as f:
            json.dump(datos_json, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Éxito", f"Archivo corregido guardado:\n{archivo_actual}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")

def fusionar_diccionarios(d1, d2):
    fusionado = dict(d1)
    for key, value in d2.items():
        if key not in fusionado or fusionado[key] in [None, "", [], {}]:
            fusionado[key] = value
        elif fusionado[key] != value:
            if isinstance(fusionado[key], list):
                if isinstance(value, list):
                    fusionado[key] = list(set(fusionado[key] + value))
                elif value not in fusionado[key]:
                    fusionado[key].append(value)
            else:
                if isinstance(value, list):
                    fusionado[key] = list(set([fusionado[key]] + value))
                elif fusionado[key] != value:
                    fusionado[key] = list(set([fusionado[key], value]))
    return fusionado

# GUI
root = tk.Tk()
root.title("Editor JSON Kanji - Detección y fusión de duplicados")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

btn_cargar = tk.Button(frame, text="📂 Cargar JSON", command=cargar_json)
btn_cargar.grid(row=0, column=0, padx=5)

btn_fusionar = tk.Button(frame, text="💾 Guardar en el mismo archivo", command=fusionar_y_guardar)
btn_fusionar.grid(row=0, column=1, padx=5)

text_area = scrolledtext.ScrolledText(root, width=100, height=30, font=("Consolas", 10))
text_area.pack(padx=10, pady=10)

root.mainloop()
