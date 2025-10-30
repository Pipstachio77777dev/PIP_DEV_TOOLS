import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json

class JSONtoTSVConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON a TSV para Anki")
        self.root.geometry("400x300")

        self.json_data = []
        self.fields = []

        self.label = tk.Label(root, text="1. Cargar archivo JSON", font=("Arial", 12))
        self.label.pack(pady=10)

        self.load_button = tk.Button(root, text="Seleccionar JSON", command=self.load_json)
        self.load_button.pack(pady=5)

        self.field_frame = tk.Frame(root)
        self.field_frame.pack(pady=10)

        self.label2 = tk.Label(root, text="2. Elegir orden de campos:", font=("Arial", 12))
        self.label2.pack()

        self.comboboxes = []

        self.export_button = tk.Button(root, text="3. Exportar TSV", command=self.export_tsv, state="disabled")
        self.export_button.pack(pady=20)

    def load_json(self):
        file_path = filedialog.askopenfilename(title="Selecciona archivo JSON", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.json_data = json.load(f)
            if not isinstance(self.json_data, list) or not self.json_data:
                raise ValueError("El JSON debe contener una lista de objetos no vacía.")
            keys = list(self.json_data[0].keys())

            # Orden preferido
            preferred_order = ["word","kanji", "furigana", "romaji",
             "pinyin", "onyomi", "kunyomi", "significado",
             "spanish", "english", "portuguese", "phrase_jp","phrase_es",
             "latin","french","german","italian","chinese","korean","russian","hindi","arabic",
             "example"]
            custom_order = [k for k in preferred_order if k in keys]
            remaining_keys = sorted([k for k in keys if k not in custom_order])
            self.fields = custom_order + remaining_keys

            self.display_field_selectors()
            self.export_button.config(state="normal")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el JSON:\n{e}")

    def display_field_selectors(self):
        for widget in self.field_frame.winfo_children():
            widget.destroy()
        self.comboboxes.clear()

        num_fields = len(self.fields)
        for i in range(num_fields):
            label = tk.Label(self.field_frame, text=f"Campo {i+1}:")
            label.grid(row=i, column=0, padx=5, pady=5, sticky="e")

            cb = ttk.Combobox(self.field_frame, values=self.fields, state="readonly")
            cb.grid(row=i, column=1, padx=5, pady=5)
            if i < len(self.fields):
                cb.set(self.fields[i])
            self.comboboxes.append(cb)

    def export_tsv(self):
        selected_order = [cb.get() for cb in self.comboboxes]
        if len(set(selected_order)) != len(selected_order):
            messagebox.showerror("Error", "Hay campos duplicados en la selección.")
            return

        tsv_lines = []
        for item in self.json_data:
            row = [str(item.get(key, "")).strip() for key in selected_order]
            tsv_lines.append("\t".join(row))

        save_path = filedialog.asksaveasfilename(defaultextension=".tsv", filetypes=[("TSV files", "*.tsv")])
        if not save_path:
            return

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write("\n".join(tsv_lines))
            messagebox.showinfo("Éxito", f"Archivo TSV guardado en:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = JSONtoTSVConverter(root)
    root.mainloop()
