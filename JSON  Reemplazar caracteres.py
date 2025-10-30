import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

# Variables globales para los fragmentos
fragmento_buscar = ""
fragmento_reemplazo = ""

# Función recursiva para reemplazar fragmentos en strings
def reemplazar_fragmentos(obj):
    if isinstance(obj, dict):
        return {k: reemplazar_fragmentos(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [reemplazar_fragmentos(elem) for elem in obj]
    elif isinstance(obj, str):
        nuevo = obj
        # Reemplazo de corchetes
        nuevo = nuevo.replace("[", "(").replace("]", ")")
        # Reemplazo dinámico del fragmento
        if fragmento_buscar:
            nuevo = nuevo.replace(fragmento_buscar, fragmento_reemplazo)
        return nuevo
    else:
        return obj

# Función para elegir el fragmento a buscar
def elegir_fragmento_buscar():
    global fragmento_buscar
    fragmento_buscar = simpledialog.askstring("Fragmento a buscar", "Ingresa el fragmento que quieres reemplazar:")
    if fragmento_buscar:
        label_buscar.config(text=f"Fragmento a buscar: '{fragmento_buscar}'")
    else:
        label_buscar.config(text="Fragmento a buscar: (ninguno)")

# Función para elegir el fragmento de reemplazo
def elegir_fragmento_reemplazo():
    global fragmento_reemplazo
    fragmento_reemplazo = simpledialog.askstring("Fragmento de reemplazo", "Ingresa el fragmento de reemplazo:")
    if fragmento_reemplazo:
        label_reemplazo.config(text=f"Fragmento de reemplazo: '{fragmento_reemplazo}'")
    else:
        label_reemplazo.config(text="Fragmento de reemplazo: (ninguno)")

# Función para procesar el JSON
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
    
    data_modificado = reemplazar_fragmentos(data)
    
    try:
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(data_modificado, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("Éxito", f"Se han aplicado los reemplazos en:\n{archivo}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el JSON:\n{e}")

# Interfaz Tkinter
root = tk.Tk()
root.title("Reemplazar fragmentos en JSON")
root.geometry("500x250")

tk.Label(root, text="Selecciona tu archivo JSON y define los reemplazos", wraplength=450).pack(pady=10)

boton_buscar = tk.Button(root, text="Elegir fragmento a buscar", command=elegir_fragmento_buscar)
boton_buscar.pack(pady=5)

label_buscar = tk.Label(root, text="Fragmento a buscar: (ninguno)")
label_buscar.pack()

boton_reemplazo = tk.Button(root, text="Elegir fragmento de reemplazo", command=elegir_fragmento_reemplazo)
boton_reemplazo.pack(pady=5)

label_reemplazo = tk.Label(root, text="Fragmento de reemplazo: (ninguno)")
label_reemplazo.pack()

boton_procesar = tk.Button(root, text="Procesar JSON", command=procesar_json)
boton_procesar.pack(pady=15)

root.mainloop()
