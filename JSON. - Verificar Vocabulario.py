import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import os

REQUIRED_KEYS = [
    "kanji",
    "furigana",
    "spanish",
    "romaji",
    "english",
    "portuguese",
    "phrase_jp",
    "phrase_es",
    "phrase_en",
    "phrase_pt",  
    "chinese",
    "korean"

]


def validar_y_corregir_json(json_data):
    errores = []
    corregido = []

    if not isinstance(json_data, list):
        errores.append("El JSON raíz debe ser un array '[...]', no un objeto '{...}'.")
        return errores, corregido

    for idx, item in enumerate(json_data, start=1):
        nuevo_item = {}
        if not isinstance(item, dict):
            errores.append(f"Línea aproximada {idx}: El elemento no es un objeto, se reemplaza por objeto vacío.")
            item = {}
        # Agregar propiedades faltantes con string vacío
        for key in REQUIRED_KEYS:
            if key not in item:
                errores.append(f"Línea aproximada {idx}: Falta la propiedad '{key}', se agrega vacía.")
                nuevo_item[key] = ""
            else:
                if not isinstance(item[key], str):
                    errores.append(f"Línea aproximada {idx}: La propiedad '{key}' no es string, se convierte a string.")
                    nuevo_item[key] = str(item[key])
                else:
                    nuevo_item[key] = item[key]

        # Ignorar propiedades extra
        extras = set(item.keys()) - set(REQUIRED_KEYS)
        if extras:
            errores.append(f"Línea aproximada {idx}: Propiedades extra eliminadas: {', '.join(extras)}")

        corregido.append(nuevo_item)

    return errores, corregido

def cargar_y_corregir():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if not file_path:
        return
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            data = json.loads(content)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer o parsear el JSON:\n{e}")
        return
    
    errores, corregido = validar_y_corregir_json(data)
    
    txt_resultados.config(state="normal")
    txt_resultados.delete(1.0, tk.END)
    
    if errores:
        txt_resultados.insert(tk.END, "Se detectaron errores y se corrigieron:\n")
        txt_resultados.insert(tk.END, "\n".join(errores))
    else:
        txt_resultados.insert(tk.END, "El JSON estaba correcto. No se necesitó corrección.")
    
    txt_resultados.config(state="disabled")
    
    # Guardar JSON corregido
    base, ext = os.path.splitext(file_path)
    corregido_path = f"{base}_corregido.json"
    try:
        with open(corregido_path, "w", encoding="utf-8") as f:
            json.dump(corregido, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("Archivo Guardado", f"JSON corregido guardado en:\n{corregido_path}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el archivo corregido:\n{e}")

# Configuración de la ventana principal
root = tk.Tk()
root.title("Validador y Corrector de JSON Kanji")
root.geometry("700x500")

btn_cargar = tk.Button(root, text="Cargar y Corregir JSON", command=cargar_y_corregir)
btn_cargar.pack(pady=10)

txt_resultados = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=25, state="disabled")
txt_resultados.pack(padx=10, pady=10)

root.mainloop()
