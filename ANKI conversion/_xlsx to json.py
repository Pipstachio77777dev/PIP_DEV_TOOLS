import subprocess
import sys

# Instala automáticamente pandas y openpyxl si no están instalados
def install_if_missing(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_if_missing("pandas")
install_if_missing("openpyxl")

# Ahora importa lo necesario
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import json
import os

class XLSXtoJSONConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Convertidor XLSX a JSON")

        self.filename = None
        self.entries = []
        self.df = None

        self.select_button = tk.Button(root, text="Seleccionar archivo XLSX", command=self.select_file)
        self.select_button.pack(pady=10)

        self.fields_frame = tk.Frame(root)
        self.fields_frame.pack()

        self.convert_button = tk.Button(root, text="Convertir a JSON", command=self.convert_to_json, state=tk.DISABLED)
        self.convert_button.pack(pady=10)

    def select_file(self):
        self.filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not self.filename:
            return

        try:
            self.df = pd.read_excel(self.filename, engine='openpyxl')
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")
            return

        self.display_fields()

    def display_fields(self):
        # Limpiar campos anteriores
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        self.entries.clear()

        tk.Label(self.fields_frame, text="Campos (edita si deseas cambiar los nombres)").pack()

        for col in self.df.columns:
            frame = tk.Frame(self.fields_frame)
            frame.pack(pady=2)

            label = tk.Label(frame, text=f"Original: {col}", width=30, anchor='w')
            label.pack(side=tk.LEFT)

            entry = tk.Entry(frame)
            entry.insert(0, col)
            entry.pack(side=tk.LEFT)
            self.entries.append(entry)

        self.convert_button.config(state=tk.NORMAL)

    def convert_to_json(self):
        new_column_names = [entry.get() for entry in self.entries]
        self.df.columns = new_column_names

        save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not save_path:
            return

        try:
            self.df.to_json(save_path, orient='records', force_ascii=False, indent=4)
            messagebox.showinfo("Éxito", f"Archivo guardado como JSON:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo JSON:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = XLSXtoJSONConverter(root)
    root.mainloop()
