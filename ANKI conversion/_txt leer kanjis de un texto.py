import tkinter as tk
from tkinter import filedialog, messagebox
import json
import re
import os

# Expresión regular para detectar Kanjis (CJK Unified Ideographs)
KANJI_REGEX = re.compile(r'[\u4E00-\u9FFF]')

def leer_txt_y_extraer_kanjis(filepath):
    """Lee un archivo txt y devuelve una lista de kanjis únicos."""
    with open(filepath, "r", encoding="utf-8") as f:
        contenido = f.read()
    kanjis = KANJI_REGEX.findall(contenido)
    return list(dict.fromkeys(kanjis))  # elimina duplicados preservando orden

def guardar_json(kanjis, output_path):
    """Guarda los kanjis en un JSON con el formato solicitado."""
    data = [{"kanji": k} for k in kanjis]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def seleccionar_archivo():
    filepath = filedialog.askopenfilename(
        title="Selecciona un archivo TXT",
        filetypes=[("Archivos de texto", "*.txt")]
    )
    if not filepath:
        return

    try:
        kanjis = leer_txt_y_extraer_kanjis(filepath)
        if not kanjis:
            messagebox.showinfo("Resultado", "No se encontraron kanjis en el archivo.")
            return

        # Guardar en mismo directorio con extensión .json
        output_path = os.path.splitext(filepath)[0] + ".json"
        guardar_json(kanjis, output_path)

        messagebox.showinfo("Éxito", f"Kanjis extraídos y guardados en:\n{output_path}")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Interfaz Tkinter
def main():
    root = tk.Tk()
    root.title("Extractor de Kanjis a JSON")
    root.geometry("400x200")

    label = tk.Label(root, text="Selecciona un archivo .txt para extraer los kanjis", wraplength=300)
    label.pack(pady=20)

    boton = tk.Button(root, text="Seleccionar archivo TXT", command=seleccionar_archivo)
    boton.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
