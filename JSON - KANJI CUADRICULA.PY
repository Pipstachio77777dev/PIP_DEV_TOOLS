import tkinter as tk
from tkinter import filedialog, messagebox
import json
import webbrowser
import os


class App:
    def __init__(self, master):
        self.master = master
        master.title("Palabras - Japonés")
        master.configure(bg="#000000")
        master.state("zoomed")

        self.datos = []
        self.actual = None
        self.ruta_json = None
        self.nombre_json = None
        self.indice_actual = None
        self.ventana_detalle = None

        # Frame principal donde estará la cuadrícula
        self.frame_principal = tk.Frame(master, bg="black")
        self.frame_principal.pack(expand=True, fill="both")

        # Menú con solo la opción de cargar JSON
        menubar = tk.Menu(master)
        archivo_menu = tk.Menu(menubar, tearoff=0)
        archivo_menu.add_command(label="Cargar JSON", command=self.cargar_archivo)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=master.quit)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)
        master.config(menu=menubar)

    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")])
        if not ruta:
            return
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                self.datos = json.load(f)
                if not isinstance(self.datos, list):
                    raise ValueError("El JSON debe contener una lista.")
            self.ruta_json = ruta
            self.nombre_json = os.path.basename(ruta)
            # Cambiar título de la ventana principal
            self.master.title(f"Palabras - Japonés | {self.nombre_json}")
            self.mostrar_cuadricula()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")

    def mostrar_cuadricula(self):
        # Limpiar pantalla antes de dibujar cuadrícula
        for widget in self.frame_principal.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(self.frame_principal, bg="black")
        scrollbar = tk.Scrollbar(self.frame_principal, orient="vertical", command=canvas.yview)
        frame_grid = tk.Frame(canvas, bg="black")

        frame_grid.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=frame_grid, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        columnas = 25
        for i, item in enumerate(self.datos):
            if isinstance(item, dict):
                texto_btn = item.get("kanji", f"Item {i+1}")
            else:
                texto_btn = f"Item {i+1}"

            btn = tk.Button(frame_grid, text=texto_btn,
                            font=("Arial", 24, "bold"),
                            width=2, height=1,
                            command=lambda idx=i: self.mostrar_detalle(idx))
            btn.grid(row=i // columnas, column=i % columnas, padx=6, pady=6)

    def mostrar_detalle(self, idx):
        self.indice_actual = idx
        self.actual = self.datos[self.indice_actual]

        if self.ventana_detalle and self.ventana_detalle.winfo_exists():
            self.ventana_detalle.destroy()

        self.ventana_detalle = tk.Toplevel(self.master)

        # Título con nombre JSON + kanji
        kanji = self.actual.get("kanji", f"Item {idx+1}")
        titulo = f"Detalle - {kanji} | {self.nombre_json}" if self.nombre_json else f"Detalle - {kanji}"
        self.ventana_detalle.title(titulo)

        self.ventana_detalle.configure(bg="black")
        self.ventana_detalle.geometry("800x700")

        if not isinstance(self.actual, dict):
            tk.Label(self.ventana_detalle, text="Datos inválidos",
                     fg="red", bg="black", font=("Arial", 20)).pack()
            return

        # ==== Scrollable Frame ====
        canvas = tk.Canvas(self.ventana_detalle, bg="black", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.ventana_detalle, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="black")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ==== Contenido ====
        tk.Label(scrollable_frame, text=self.actual.get("kanji", ""),
                 font=("Arial", 100, "bold"), fg="white", bg="black").pack(pady=20)

        # Botón guardar arriba
        tk.Button(scrollable_frame, text="💾 Guardar cambios",
                  command=self.guardar_cambios,
                  bg="green", fg="white", font=("Arial", 14, "bold")).pack(pady=10)

        self.campos = {}
        campos_texto = ["pinyin", "onyomi", "kunyomi", "spanish", "english", "example"]

        for campo in campos_texto:
            tk.Label(scrollable_frame, text=campo.capitalize(), fg="white",
                     bg="black", font=("Arial", 14, "bold"), anchor="w").pack(fill="x", padx=20, pady=(10, 0))

            valor = self.actual.get(campo, "")

            # Si es un campo largo -> Text
            if campo in ["spanish", "english", "example"]:
                txt = tk.Text(scrollable_frame, wrap="word", height=4,
                              font=("Arial", 13), bg="#111", fg="white", insertbackground="white")
                txt.insert("1.0", valor)
                txt.pack(fill="x", padx=20, pady=5)
                self.campos[campo] = txt
            else:
                entry = tk.Entry(scrollable_frame, font=("Arial", 13),
                                 bg="#111", fg="white", insertbackground="white")
                entry.insert(0, valor)
                entry.pack(fill="x", padx=20, pady=5)
                self.campos[campo] = entry

        # Botón Jisho al final
        if self.actual.get("kanji"):
            tk.Button(scrollable_frame, text="📖 Abrir en Jisho",
                      command=lambda: webbrowser.open(f"https://jisho.org/search/{self.actual['kanji']}"),
                      bg="#333", fg="white", font=("Arial", 14, "bold")).pack(pady=15)

    def guardar_cambios(self):
        if self.indice_actual is None:
            return

        for campo, widget in self.campos.items():
            if isinstance(widget, tk.Text):
                self.actual[campo] = widget.get("1.0", "end-1c").strip()
            else:
                self.actual[campo] = widget.get().strip()

        self.datos[self.indice_actual] = self.actual

        if self.ruta_json:
            try:
                with open(self.ruta_json, "w", encoding="utf-8") as f:
                    json.dump(self.datos, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Guardado", "Cambios guardados correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
