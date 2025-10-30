import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

datos_json = []
ruta_actual = None  # Para guardar la ruta del archivo cargado

def cargar_json():
    global datos_json, ruta_actual
    ruta = filedialog.askopenfilename(
        filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
    )
    if not ruta:
        return
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos_json = json.load(f)
        ruta_actual = ruta
        mostrar_resultado(datos_json)
        messagebox.showinfo("Carga exitosa", f"Archivo cargado: {ruta}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el archivo JSON:\n{e}")

def mostrar_resultado(datos):
    texto.delete("1.0", tk.END)
    texto.insert(tk.END, json.dumps(datos, ensure_ascii=False, indent=2))

def ordenar_json():
    if not datos_json:
        messagebox.showwarning("Atención", "Primero carga un archivo JSON.")
        return
    try:
        ordenado = sorted(datos_json, key=lambda x: str(x.get("kanji", "")))
        mostrar_resultado(ordenado)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo ordenar el JSON:\n{e}")

def aplicar_cambios():
    global datos_json, ruta_actual
    if not datos_json:
        messagebox.showwarning("Atención", "Primero carga un archivo JSON.")
        return
    if not ruta_actual:
        messagebox.showwarning("Atención", "No hay archivo cargado para guardar.")
        return
    try:
        especial = "こにちは"
        especial_entries = [d for d in datos_json if str(d.get("kanji", "")) == especial]
        resto = [d for d in datos_json if str(d.get("kanji", "")) != especial]

        resto_ordenado = sorted(resto, key=lambda x: str(x.get("kanji", "")))

        datos_json = especial_entries + resto_ordenado

        # Guardar archivo reescribiendo el JSON ordenado
        with open(ruta_actual, "w", encoding="utf-8") as f:
            json.dump(datos_json, f, ensure_ascii=False, indent=2)

        mostrar_resultado(datos_json)
        messagebox.showinfo("Listo", f"JSON ordenado y guardado.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo aplicar los cambios:\n{e}")

root = tk.Tk()
root.title("Alfabetizador JSON")

frame_botones = tk.Frame(root)
frame_botones.pack(pady=10)

btn_cargar = tk.Button(frame_botones, text="Cargar JSON", command=cargar_json)
btn_cargar.pack(side=tk.LEFT, padx=5)

btn_ordenar = tk.Button(frame_botones, text="Ordenar", command=ordenar_json)
btn_ordenar.pack(side=tk.LEFT, padx=5)

btn_aplicar = tk.Button(frame_botones, text="Aplicar Cambios", command=aplicar_cambios)
btn_aplicar.pack(side=tk.LEFT, padx=5)

texto = scrolledtext.ScrolledText(root, width=80, height=30)
texto.pack(padx=10, pady=10)

root.mainloop()
