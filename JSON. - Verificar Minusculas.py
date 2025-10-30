import json
import tkinter as tk
from tkinter import filedialog, messagebox

def convert_to_lowercase(data):
    """
    Convierte recursivamente todos los strings del JSON a minúsculas.
    """
    if isinstance(data, dict):
        return {k: convert_to_lowercase(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_to_lowercase(item) for item in data]
    elif isinstance(data, str):
        return data.lower()
    else:
        return data

def open_file():
    file_path = filedialog.askopenfilename(
        title="Selecciona un archivo JSON",
        filetypes=[("JSON Files", "*.json")]
    )
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convertir a minúsculas
            data_lower = convert_to_lowercase(data)
            
            # Guardar de nuevo
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_lower, f, ensure_ascii=False, indent=4)
            
            messagebox.showinfo("Éxito", f"Archivo procesado y guardado:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar el archivo:\n{e}")

# Configuración de la ventana Tkinter
root = tk.Tk()
root.title("JSON a minúsculas")

root.geometry("300x150")

btn_open = tk.Button(root, text="Abrir JSON", command=open_file)
btn_open.pack(pady=50)

root.mainloop()
