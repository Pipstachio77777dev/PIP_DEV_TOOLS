import tkinter as tk
from tkinter import filedialog, messagebox
import json
import sys

class KanjiReorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reorder Kanji from JSON")

        try:
            self.root.state("zoomed")
        except Exception:
            pass

        self.kanji_list = []
        self.current_file_path = None
        self.highlight_index = None  # <-- Guardar índice del kanji encontrado

        # Top buttons
        top_frame = tk.Frame(root)
        top_frame.pack(fill="x", padx=6, pady=6)

        tk.Button(top_frame, text="Load JSON", font=("Arial", 14), command=self.load_json).pack(side="left", padx=4)
        tk.Button(top_frame, text="Save JSON", font=("Arial", 14), command=self.save_json).pack(side="left", padx=4)

        # Campo de búsqueda
        tk.Label(top_frame, text="Buscar Kanji:", font=("Arial", 12)).pack(side="left", padx=(20,4))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.search_kanji())
        search_entry = tk.Entry(top_frame, textvariable=self.search_var, font=("Arial", 14), width=15)
        search_entry.pack(side="left", padx=4)

        # Scroll container
        container = tk.Frame(root)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.list_frame = tk.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")

        self.list_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.window_id, width=e.width))

        if sys.platform == "darwin":
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_mac)
        else:
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
            self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
            self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def _on_mousewheel_mac(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta), "units")

    def load_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list) and all(isinstance(item, dict) and "kanji" in item for item in data):
                self.kanji_list = data
                self.current_file_path = path
            else:
                messagebox.showerror("Error", "El JSON debe ser una lista de objetos y cada objeto debe tener la clave 'kanji'.")
                return

            self.refresh_list()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")

    def save_json(self):
        if not self.kanji_list:
            messagebox.showwarning("Aviso", "No hay datos para guardar.")
            return

        if not self.current_file_path:
            path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
            if not path:
                return
            self.current_file_path = path

        try:
            with open(self.current_file_path, "w", encoding="utf-8") as f:
                json.dump(self.kanji_list, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Éxito", f"JSON guardado correctamente en:\n{self.current_file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

    def refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        for idx, item in enumerate(self.kanji_list):
            row = tk.Frame(self.list_frame)
            row.pack(fill="x", pady=4, padx=8)

            idx_var = tk.StringVar(value=str(idx + 1))
            idx_entry = tk.Entry(row, textvariable=idx_var, font=("Arial", 18, "bold"), width=4, justify="center")
            idx_entry.pack(side="left")
            idx_entry.bind("<Return>", lambda e, i=idx, var=idx_var: self.change_index(i, var))
            idx_entry.bind("<FocusOut>", lambda e, i=idx, var=idx_var: self.change_index(i, var))

            btn_up = tk.Button(row, text="↑", font=("Arial", 14), width=3, command=lambda i=idx: self.move_up(i))
            btn_up.pack(side="left", padx=2)
            btn_down = tk.Button(row, text="↓", font=("Arial", 14), width=3, command=lambda i=idx: self.move_down(i))
            btn_down.pack(side="left", padx=2)

            # Destacar si es el encontrado
            bg_color = "yellow" if self.highlight_index == idx else None
            kanji_lbl = tk.Label(row, text=item.get("kanji", ""), font=("Arial", 32), anchor="center", bg=bg_color)
            kanji_lbl.pack(side="left", fill="x", expand=True)

    def search_kanji(self):
        search_text = self.search_var.get().strip()
        self.highlight_index = None
        if search_text:
            for i, k in enumerate(self.kanji_list):
                if k.get("kanji") == search_text:
                    self.highlight_index = i
                    messagebox.showinfo("Resultado", f"Kanji '{search_text}' encontrado en la posición: {i + 1}")
                    break
            else:
                messagebox.showwarning("No encontrado", f"El kanji '{search_text}' no está en la lista.")
        self.refresh_list()

    def change_index(self, old_index, idx_var):
        try:
            new_pos = int(idx_var.get()) - 1
        except ValueError:
            idx_var.set(str(old_index + 1))
            return

        if new_pos < 0 or new_pos >= len(self.kanji_list):
            messagebox.showwarning("Índice inválido", f"El índice debe estar entre 1 y {len(self.kanji_list)}")
            idx_var.set(str(old_index + 1))
            return

        if new_pos == old_index:
            return

        item = self.kanji_list.pop(old_index)
        self.kanji_list.insert(new_pos, item)
        self.refresh_list()

    def move_up(self, index):
        if index > 0:
            self.kanji_list[index], self.kanji_list[index - 1] = (
                self.kanji_list[index - 1],
                self.kanji_list[index],
            )
            self.refresh_list()

    def move_down(self, index):
        if index < len(self.kanji_list) - 1:
            self.kanji_list[index], self.kanji_list[index + 1] = (
                self.kanji_list[index + 1],
                self.kanji_list[index],
            )
            self.refresh_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = KanjiReorderApp(root)
    root.mainloop()
