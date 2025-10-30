import tkinter as tk
from tkinter import filedialog, messagebox, font
import json
import webbrowser
import os

class JsonComparerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparador de JSON por campo (No coincidencias)")

        # Colores y estilos
        self.bg_color = "#f2f7fd"
        self.fg_color = "#116eef"
        self.btn_bg = "#116eef"
        self.btn_fg = "#FFFFFF"
        self.highlight_bg = "orange"

        self.root.configure(bg=self.bg_color)

        # Datos JSON
        self.json_data_1 = None
        self.json_data_2 = None
        self.filename_1 = None
        self.filename_2 = None

        self.diff_values_json1 = set()
        self.diff_values_json2 = set()

        self.result_font = font.Font(family="Consolas", size=16)

        # UI
        self.label1 = tk.Label(root, text="Archivo JSON 1: No cargado", bg=self.bg_color, fg=self.fg_color)
        self.label1.pack(pady=5)

        self.records_label_1 = tk.Label(root, text="Registros JSON 1: 0", bg=self.bg_color, fg=self.fg_color)
        self.records_label_1.pack(pady=(0,5))

        self.btn_load1 = tk.Button(root, text="Cargar JSON 1", command=self.load_json1,
                                   bg=self.btn_bg, fg=self.btn_fg, activebackground=self.highlight_bg)
        self.btn_load1.pack(pady=5)

        self.label2 = tk.Label(root, text="Archivo JSON 2: No cargado", bg=self.bg_color, fg=self.fg_color)
        self.label2.pack(pady=5)

        self.records_label_2 = tk.Label(root, text="Registros JSON 2: 0", bg=self.bg_color, fg=self.fg_color)
        self.records_label_2.pack(pady=(0,5))

        self.btn_load2 = tk.Button(root, text="Cargar JSON 2", command=self.load_json2,
                                   bg=self.btn_bg, fg=self.btn_fg, activebackground=self.highlight_bg)
        self.btn_load2.pack(pady=5)

        self.fields_label = tk.Label(root, text="Campo común para comparar:", bg=self.bg_color, fg=self.fg_color)
        self.fields_label.pack(pady=5)
        self.field_var = tk.StringVar(root)
        self.field_dropdown = tk.OptionMenu(root, self.field_var, "")
        self.field_dropdown.config(bg=self.btn_bg, fg=self.btn_fg, activebackground=self.highlight_bg, activeforeground=self.btn_fg)
        self.field_dropdown["menu"].config(bg=self.btn_bg, fg=self.btn_fg)
        self.field_dropdown.pack(pady=5)

        self.btn_compare = tk.Button(root, text="Comparar valores del campo", command=self.compare_field_values,
                                     bg=self.btn_bg, fg=self.btn_fg, activebackground=self.highlight_bg)
        self.btn_compare.pack(pady=10)

        self.results_container = tk.Frame(root, bg=self.bg_color)
        self.results_container.pack(fill="both", expand=True, pady=10)

        # Columnas para NO coincidencias
        self.left_frame = tk.Frame(self.results_container, bg=self.bg_color)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=10)

        self.left_label_title = tk.Label(self.left_frame, text="Exclusivos JSON 1",
                                         bg=self.bg_color, fg=self.fg_color, font=("Consolas", 14, "bold"))
        self.left_label_title.pack(pady=(0,5))

        self.left_canvas = tk.Canvas(self.left_frame, bg="#121212", highlightthickness=0)
        self.left_canvas.pack(side="left", fill="both", expand=True)

        self.left_scrollbar = tk.Scrollbar(self.left_frame, orient="vertical", command=self.left_canvas.yview)
        self.left_scrollbar.pack(side="right", fill="y")
        self.left_canvas.configure(yscrollcommand=self.left_scrollbar.set)

        self.left_diff_frame = tk.Frame(self.left_canvas, bg="#121212")
        self.left_canvas.create_window((0, 0), window=self.left_diff_frame, anchor="nw")
        self.left_diff_frame.bind("<Configure>", lambda e: self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all")))

        self.right_frame = tk.Frame(self.results_container, bg=self.bg_color)
        self.right_frame.pack(side="left", fill="both", expand=True, padx=10)

        self.right_label_title = tk.Label(self.right_frame, text="Exclusivos JSON 2",
                                          bg=self.bg_color, fg=self.fg_color, font=("Consolas", 14, "bold"))
        self.right_label_title.pack(pady=(0,5))

        self.right_canvas = tk.Canvas(self.right_frame, bg="#121212", highlightthickness=0)
        self.right_canvas.pack(side="left", fill="both", expand=True)

        self.right_scrollbar = tk.Scrollbar(self.right_frame, orient="vertical", command=self.right_canvas.yview)
        self.right_scrollbar.pack(side="right", fill="y")
        self.right_canvas.configure(yscrollcommand=self.right_scrollbar.set)

        self.right_diff_frame = tk.Frame(self.right_canvas, bg="#121212")
        self.right_canvas.create_window((0, 0), window=self.right_diff_frame, anchor="nw")
        self.right_diff_frame.bind("<Configure>", lambda e: self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all")))

    # ---------- Cargar JSON ----------
    def load_json1(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.json_data_1 = json.load(f)
            self.label1.config(text=f"JSON 1: {path}")
            self.filename_1 = path
            self.update_records_label(1)
            self.check_and_update_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando JSON 1:\n{e}")

    def load_json2(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.json_data_2 = json.load(f)
            self.label2.config(text=f"JSON 2: {path}")
            self.filename_2 = path
            self.update_records_label(2)
            self.check_and_update_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando JSON 2:\n{e}")

    def update_records_label(self, json_number):
        data = self.json_data_1 if json_number == 1 else self.json_data_2
        count = 0
        if isinstance(data, list):
            count = len(data)
        elif isinstance(data, dict):
            count = len(data)
        if json_number == 1:
            self.records_label_1.config(text=f"Registros JSON 1: {count}")
        else:
            self.records_label_2.config(text=f"Registros JSON 2: {count}")

    # ---------- Extraer claves y valores ----------
    def extract_keys(self, data):
        if isinstance(data, dict):
            return set(data.keys())
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            return set(data[0].keys())
        return set()

    def extract_values_by_key(self, data, key):
        values = set()
        if isinstance(data, dict):
            value = data.get(key)
            if value is not None:
                values.add(str(value))
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    value = item.get(key)
                    if value is not None:
                        values.add(str(value))
        return values

    # ---------- Actualizar menú de campos ----------
    def check_and_update_fields(self):
        if not self.json_data_1 or not self.json_data_2:
            return

        keys1 = self.extract_keys(self.json_data_1)
        keys2 = self.extract_keys(self.json_data_2)
        common_fields = list(keys1.intersection(keys2))

        if not common_fields:
            messagebox.showwarning("Advertencia", "No hay campos en común entre los dos JSON.")
            return

        common_fields.sort(key=lambda x: (0 if x.lower() == "kanji" else 1, x))

        menu = self.field_dropdown["menu"]
        menu.delete(0, "end")
        for field in common_fields:
            menu.add_command(label=field, command=lambda f=field: self.field_var.set(f))

        self.field_var.set(common_fields[0])

    # ---------- Comparar valores NO coincidentes ----------
    def compare_field_values(self):
        if not self.json_data_1 or not self.json_data_2:
            messagebox.showwarning("Advertencia", "Debes cargar ambos archivos JSON.")
            return

        field = self.field_var.get()
        if not field:
            messagebox.showwarning("Advertencia", "Selecciona un campo para comparar.")
            return

        values1 = self.extract_values_by_key(self.json_data_1, field)
        values2 = self.extract_values_by_key(self.json_data_2, field)

        # Valores exclusivos
        self.diff_values_json1 = values1 - values2
        self.diff_values_json2 = values2 - values1

        # Limpiar frames
        for widget in self.left_diff_frame.winfo_children():
            widget.destroy()
        for widget in self.right_diff_frame.winfo_children():
            widget.destroy()

        # Mostrar valores JSON 1
        for val in sorted(self.diff_values_json1):
            frame = tk.Frame(self.left_diff_frame, bg="#121212")
            frame.pack(fill="x", pady=2)
            btn = tk.Button(frame, text=val, font=self.result_font, fg="white", bg="#116eef",
                            activebackground="#333333", activeforeground="#00BFFF", borderwidth=0,
                            cursor="hand2", command=lambda v=val: self.open_link_and_copy(v))
            btn.pack(side="left", padx=5, fill="x", expand=True)
            transfer_btn = tk.Button(frame, text="→ JSON 2", bg=self.btn_bg, fg=self.btn_fg,
                                     command=lambda v=val: self.transfer_value(v, 1))
            transfer_btn.pack(side="left", padx=5)

        # Mostrar valores JSON 2
        for val in sorted(self.diff_values_json2):
            frame = tk.Frame(self.right_diff_frame, bg="#121212")
            frame.pack(fill="x", pady=2)
            btn = tk.Button(frame, text=val, font=self.result_font, fg="white", bg="#116eef",
                            activebackground="#333333", activeforeground="#00BFFF", borderwidth=0,
                            cursor="hand2", command=lambda v=val: self.open_link_and_copy(v))
            btn.pack(side="left", padx=5, fill="x", expand=True)
            transfer_btn = tk.Button(frame, text="→ JSON 1", bg=self.btn_bg, fg=self.btn_fg,
                                     command=lambda v=val: self.transfer_value(v, 2))
            transfer_btn.pack(side="left", padx=5)

    # ---------- Transferir valor al otro JSON (mover) ----------
    def transfer_value(self, value, from_json_number):
        # Determinar origen y destino
        if from_json_number == 1:
            source_data = self.json_data_1
            target_data = self.json_data_2
        else:
            source_data = self.json_data_2
            target_data = self.json_data_1

        field = self.field_var.get()

        # ---- Eliminar del JSON origen ----
        if isinstance(source_data, list):
            source_data[:] = [item for item in source_data if str(item.get(field)) != value]
        elif isinstance(source_data, dict):
            if str(source_data.get(field)) == value:
                source_data.clear()

        # ---- Agregar al JSON destino ----
        if isinstance(target_data, list):
            target_data.append({field: value})
        elif isinstance(target_data, dict):
            target_data[field] = value

        # ---- Guardar archivos ----
        self.save_jsons()

        # ---- Actualizar UI ----
        self.compare_field_values()

    # ---------- Guardar JSON ----------
    def save_jsons(self):
        try:
            if self.filename_1 and isinstance(self.json_data_1, (dict, list)):
                with open(self.filename_1, "w", encoding="utf-8") as f:
                    json.dump(self.json_data_1, f, ensure_ascii=False, indent=4)
            if self.filename_2 and isinstance(self.json_data_2, (dict, list)):
                with open(self.filename_2, "w", encoding="utf-8") as f:
                    json.dump(self.json_data_2, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar los JSON:\n{e}")

    # ---------- Copiar y abrir enlace ----------
    def open_link_and_copy(self, text):
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            webbrowser.open_new_tab(f"https://jisho.org/search/{text}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar o abrir el enlace:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = JsonComparerApp(root)
    root.mainloop()
