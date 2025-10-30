import tkinter as tk
from tkinter import filedialog, messagebox, font
import json
import webbrowser
import os

class JsonComparerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparador de JSON por campo")

        self.bg_color = "#f2f7fd"
        self.fg_color = "#116eef"
        self.btn_bg = "#116eef"
        self.btn_fg = "#FFFFFF"
        self.highlight_bg = "orange"

        self.root.configure(bg=self.bg_color)

        self.json_data_1 = None
        self.json_data_2 = None
        self.filename_1 = None
        self.filename_2 = None
        self.common_values = set()

        self.result_font = font.Font(family="Consolas", size=16)

        self.label1 = tk.Label(root, text="Archivo JSON 1: No cargado", bg=self.bg_color, fg=self.fg_color)
        self.label1.pack(pady=5)

        # Nueva etiqueta para mostrar cantidad registros JSON 1
        self.records_label_1 = tk.Label(root, text="Registros JSON 1: 0", bg=self.bg_color, fg=self.fg_color)
        self.records_label_1.pack(pady=(0,5))

        self.btn_load1 = tk.Button(root, text="Cargar JSON 1", command=self.load_json1,
                                   bg=self.btn_bg, fg=self.btn_fg, activebackground=self.highlight_bg)
        self.btn_load1.pack(pady=5)

        self.label2 = tk.Label(root, text="Archivo JSON 2: No cargado", bg=self.bg_color, fg=self.fg_color)
        self.label2.pack(pady=5)

        # Nueva etiqueta para mostrar cantidad registros JSON 2
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

        self.btn_merge = tk.Button(root, text="Abrir ventana de fusión", command=self.open_merge_window,
                                   bg=self.btn_bg, fg=self.btn_fg, activebackground=self.highlight_bg)
        self.btn_merge.pack(pady=10)

        self.matches_label = tk.Label(root, text="Cantidad de coincidencias: 0", bg=self.bg_color, fg=self.fg_color,
                                      font=("Consolas", 14))
        self.matches_label.pack(pady=(0,10))

        self.results_container = tk.Frame(root, bg=self.bg_color)
        self.results_container.pack(fill="both", expand=True, pady=10)

        left_frame = tk.Frame(self.results_container, bg=self.bg_color)
        left_frame.pack(side="left", fill="both", expand=True, padx=10)

        self.left_label_title = tk.Label(left_frame, text="Listado original (texto):",
                              bg=self.bg_color, fg=self.fg_color, font=("Consolas", 14, "bold"))
        self.left_label_title.pack(pady=(0,5))

        self.left_text = tk.Text(left_frame, height=20, width=40, bg="#121212", fg=self.fg_color,
                                 font=self.result_font, state="disabled", wrap="word", insertbackground=self.fg_color)
        self.left_text.pack(side="left", fill="both", expand=True)

        left_scroll = tk.Scrollbar(left_frame, command=self.left_text.yview)
        left_scroll.pack(side="right", fill="y")
        self.left_text.config(yscrollcommand=left_scroll.set)

        right_frame = tk.Frame(self.results_container, bg=self.bg_color)
        right_frame.pack(side="left", fill="both", expand=True, padx=10)

        self.right_label_title = tk.Label(right_frame, text="Botones (clic para abrir + copiar):",
                               bg=self.bg_color, fg=self.fg_color, font=("Consolas", 14, "bold"))
        self.right_label_title.pack(pady=(0,5))

        self.canvas = tk.Canvas(right_frame, bg="#121212", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.result_frame = tk.Frame(self.canvas, bg="#121212")
        self.canvas.create_window((0, 0), window=self.result_frame, anchor="nw")

        self.result_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

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
        # Actualizar la etiqueta correspondiente
        if json_number == 1:
            self.records_label_1.config(text=f"Registros JSON 1: {count}")
        else:
            self.records_label_2.config(text=f"Registros JSON 2: {count}")

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
        self.common_values = values1.intersection(values2)

        count = len(self.common_values)
        self.matches_label.config(text=f"Cantidad de coincidencias: {count}")

        self.left_text.config(state="normal")
        self.left_text.delete("1.0", tk.END)
        if self.common_values:
            self.left_text.insert(tk.END, f"Valores del campo '{field}' presentes en ambos JSON:\n\n")
            for val in sorted(self.common_values):
                self.left_text.insert(tk.END, f"- {val}\n")
        else:
            self.left_text.insert(tk.END, f"No hay valores comunes para el campo '{field}'.")
        self.left_text.config(state="disabled")

        for widget in self.result_frame.winfo_children():
            widget.destroy()

        if self.common_values:
            for val in sorted(self.common_values):
                btn = tk.Button(self.result_frame, text=val, font=self.result_font, fg="white", bg="#116eef",
                                activebackground="#333333", activeforeground="#00BFFF", borderwidth=0,
                                cursor="hand2", command=lambda v=val: self.open_link_and_copy(v))
                btn.pack(anchor="center", pady=2, fill="x", expand=True)

    def open_merge_window(self):
        if not self.common_values:
            messagebox.showinfo("Sin coincidencias", "Primero realiza la comparación de campos.")
            return

        win = tk.Toplevel(self.root)
        win.title("La fusión")
        win.configure(bg=self.bg_color)

        tk.Label(win, text="Selecciona dónde conservar cada valor:",
                 fg=self.fg_color, bg=self.bg_color,
                 font=self.result_font).pack(pady=10)

        field = self.field_var.get()

        for val in sorted(self.common_values):
            frame = tk.Frame(win, bg=self.bg_color)
            frame.pack(fill="x", padx=10, pady=5)

            inner = tk.Frame(frame, bg=self.bg_color)
            inner.pack(anchor="center")

            val_btn = tk.Button(inner, text=val, font=self.result_font, fg="white", bg="#116eef",
                                activebackground="#333333", activeforeground="#00BFFF", borderwidth=0,
                                cursor="hand2", command=lambda v=val: self.open_link_and_copy(v))
            val_btn.pack(side="left", padx=10)

            btn1 = tk.Button(inner, text=f"Guardar en {os.path.basename(self.filename_1)}" if self.filename_1 else "Guardar en JSON 1", bg=self.btn_bg, fg=self.btn_fg,
                             font=self.result_font,
                             command=lambda v=val: self.keep_in_json(v, field, 1, win))
            btn1.pack(side="left", padx=5)

            btn2 = tk.Button(inner, text=f"Guardar en {os.path.basename(self.filename_2)}" if self.filename_2 else "Guardar en JSON 2", bg=self.btn_bg, fg=self.btn_fg,
                             font=self.result_font,
                             command=lambda v=val: self.keep_in_json(v, field, 2, win))
            btn2.pack(side="left", padx=5)

    def keep_in_json(self, value, field, keep_json_number, win):
        def remove_value_from_json(json_data):
            if isinstance(json_data, list):
                return [item for item in json_data if str(item.get(field)) != value]
            elif isinstance(json_data, dict):
                if str(json_data.get(field)) == value:
                    return {}
                else:
                    return json_data
            else:
                return json_data

        if keep_json_number == 1:
            self.json_data_2 = remove_value_from_json(self.json_data_2)
        else:
            self.json_data_1 = remove_value_from_json(self.json_data_1)

        try:
            if self.filename_1 and self.filename_1.endswith(".json"):
                with open(self.filename_1, "w", encoding="utf-8") as f:
                    json.dump(self.json_data_1, f, ensure_ascii=False, indent=4)
            if self.filename_2 and self.filename_2.endswith(".json"):
                with open(self.filename_2, "w", encoding="utf-8") as f:
                    json.dump(self.json_data_2, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar los JSON:\n{e}")

        self.common_values.discard(value)

        win.destroy()
        self.compare_field_values()
        self.open_merge_window()

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
