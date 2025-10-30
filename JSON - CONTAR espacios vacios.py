import json
import tkinter as tk
from tkinter import filedialog, messagebox

def cargar_json():
    ruta = filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")])
    if not ruta:
        return None
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            messagebox.showerror("Error", "El JSON debe contener una lista de objetos (diccionarios).")
            return None
        return data
    except Exception as e:
        messagebox.showerror("Error al leer JSON", str(e))
        return None

def detectar_campos(json_data):
    campos = set()
    for item in json_data:
        if isinstance(item, dict):
            campos.update(item.keys())
    return list(campos)

def encontrar_indices_vacios(json_data, campo):
    vacios = []
    for i, item in enumerate(json_data):
        valor = item.get(campo, None)
        if valor in [None, '', [], {}]:
            vacios.append(i)
    return vacios

def seleccionar_archivo():
    global data_json, campos_disponibles
    data_json = cargar_json()
    if data_json:
        campos = detectar_campos(data_json)
        if not campos:
            messagebox.showwarning("Advertencia", "No se detectaron campos en el JSON.")
            return
        variable_opcion.set(campos[0])
        menu_campo['menu'].delete(0, 'end')
        for campo in campos:
            menu_campo['menu'].add_command(label=campo, command=tk._setit(variable_opcion, campo))
        boton_buscar.config(state="normal")
        resultado_text.delete(1.0, tk.END)
        resultado_text.insert(tk.END, f"✔️ JSON cargado correctamente. Campos detectados: {len(campos)}\n")

def buscar_vacios():
    campo = variable_opcion.get()
    if not campo or not data_json:
        messagebox.showwarning("Advertencia", "Debe seleccionar un campo válido.")
        return
    indices = encontrar_indices_vacios(data_json, campo)
    resultado_text.delete(1.0, tk.END)
    resultado_text.insert(tk.END, f"🔍 Campo seleccionado: {campo}\n")
    resultado_text.insert(tk.END, f"Total de elementos vacíos: {len(indices)}\n")
    if indices:
        resultado_text.insert(tk.END, f"Índices con valores vacíos: {indices}\n")
    else:
        resultado_text.insert(tk.END, "✅ No se encontraron campos vacíos.")

# Interfaz gráfica
root = tk.Tk()
root.title("Detector de campos vacíos en JSON")
root.geometry("600x400")

data_json = None
campos_disponibles = []

frame_top = tk.Frame(root)
frame_top.pack(pady=10)

boton_cargar = tk.Button(frame_top, text="📂 Cargar JSON", command=seleccionar_archivo)
boton_cargar.pack(side=tk.LEFT, padx=10)

variable_opcion = tk.StringVar(root)
menu_campo = tk.OptionMenu(frame_top, variable_opcion, "")
menu_campo.pack(side=tk.LEFT, padx=10)

boton_buscar = tk.Button(frame_top, text="🔍 Buscar vacíos", state="disabled", command=buscar_vacios)
boton_buscar.pack(side=tk.LEFT, padx=10)

resultado_text = tk.Text(root, wrap="word", height=15)
resultado_text.pack(padx=10, pady=10, fill="both", expand=True)

root.mainloop()
