import json
import tkinter as tk
from tkinter import filedialog, messagebox

# Función recursiva para reemplazar corchetes por paréntesis
def reemplazar_corchetes(obj):
    if isinstance(obj, dict):
        return {k: reemplazar_corchetes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [reemplazar_corchetes(elem) for elem in obj]
    elif isinstance(obj, str):
        return obj.replace("[", "(").replace("]", ")")
    else:
        return obj

# Función que se ejecuta al presionar el botón
def procesar_json():
    archivo = filedialog.askopenfilename(
        title="Selecciona un archivo JSON",
        filetypes=[("Archivos JSON", "*.json")]
    )
    if not archivo:
        return  # El usuario canceló
    
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el JSON:\n{e}")
        return
    
    # Reemplazamos corchetes por paréntesis
    data_modificado = reemplazar_corchetes(data)
    
    try:
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(data_modificado, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("Éxito", f"Se han reemplazado corchetes por paréntesis en:\n{archivo}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el JSON:\n{e}")

# Interfaz con Tkinter
root = tk.Tk()
root.title("Reemplazar corchetes por paréntesis en JSON")
root.geometry("400x150")

label = tk.Label(root, text="Haz clic en el botón para seleccionar tu archivo JSON", wraplength=350)
label.pack(pady=20)

boton = tk.Button(root, text="Seleccionar archivo JSON", command=procesar_json)
boton.pack(pady=10)

root.mainloop()
