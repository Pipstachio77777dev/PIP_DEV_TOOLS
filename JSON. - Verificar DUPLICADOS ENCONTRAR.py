import json
import tkinter as tk
from tkinter import filedialog, messagebox

class JsonEditorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Editor de Palabras JSON")

        self.data = []
        self.bg_color = "#000000"
        self.fg_color = "#00ff00"

        self.frame = tk.Frame(master, padx=20, pady=20, bg=self.bg_color)
        self.frame.pack(fill="both", expand=True)

        self.btn_cargar = tk.Button(self.frame, text="Cargar JSON", command=self.cargar_json,
                                   bg=self.bg_color, fg=self.fg_color, width=20)
        self.btn_cargar.pack(pady=10)

        # Frame con canvas para scroll
        self.result_frame = tk.Frame(self.frame, bg=self.bg_color)
        self.result_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.result_frame, bg=self.bg_color, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.result_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_color)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.label_repetidos = tk.Label(self.scrollable_frame, text="", font=("Arial", 14),
                                       bg=self.bg_color, fg=self.fg_color, justify="left")
        self.label_repetidos.pack(padx=5, pady=5, anchor="nw")

        self.btn_copiar_primero = tk.Button(self.frame, text="Copiar primer kanji duplicado",
                                            command=self.copiar_primero,
                                            bg=self.bg_color, fg=self.fg_color, width=25)
        self.btn_copiar_primero.pack(pady=10)

        self.kanjis_repetidos = {}

    def cargar_json(self):
        filepath = filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")])
        if not filepath:
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            self.mostrar_kanjis_repetidos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")

    def mostrar_kanjis_repetidos(self):
        kanji_indices = {}
        for i, entry in enumerate(self.data):
            kanji = entry.get("kanji")
            if kanji:
                kanji_indices.setdefault(kanji, []).append(i)

        self.kanjis_repetidos = {k: v for k, v in kanji_indices.items() if len(v) > 1}

        if not self.kanjis_repetidos:
            self.label_repetidos.config(text="No hay kanjis repetidos.")
        else:
            texto = "Kanjis repetidos con sus índices:\n"
            for kanji, indices in self.kanjis_repetidos.items():
                texto += f"{kanji}: {indices}\n"
            self.label_repetidos.config(text=texto)

    def copiar_primero(self):
        if not self.kanjis_repetidos:
            messagebox.showinfo("Copiar", "No hay kanjis repetidos para copiar.")
            return
        primer_kanji = next(iter(self.kanjis_repetidos))
        self.master.clipboard_clear()
        self.master.clipboard_append(primer_kanji)
        messagebox.showinfo("Copiar", f"Primer kanji duplicado '{primer_kanji}' copiado al portapapeles.")

if __name__ == "__main__":
    root = tk.Tk()
    app = JsonEditorApp(root)
    root.mainloop()
