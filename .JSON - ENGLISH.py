import tkinter as tk
from tkinter import filedialog, messagebox
import random
import json
import webbrowser

class App:
    def __init__(self, master):
        self.master = master
        master.title("Palabras Aleatorias - General")
        master.configure(bg="#116eef")
        master.state("zoomed")

        self.datos = []
        self.actual = None
        self.ruta_json = None
        self.indice_actual = None

        self.frame_botones = tk.Frame(master, bg="#116eef")
        self.frame_botones.pack(fill="x", pady=10)

        self.frame_izquierda = tk.Frame(self.frame_botones, bg="#116eef")
        self.frame_izquierda.pack(side="left")

        self.frame_derecha = tk.Frame(self.frame_botones, bg="#116eef")
        self.frame_derecha.pack(side="right")

        self.btn_cargar = tk.Button(self.frame_izquierda, text="Cargar archivo JSON", command=self.cargar_archivo)
        self.btn_cargar.pack(side="left", padx=5)

        self.btn_recargar = tk.Button(self.frame_izquierda, text="Recargar JSON", command=self.recargar_json, state=tk.DISABLED)
        self.btn_recargar.pack(side="left", padx=5)

        self.btn_copiar = tk.Button(self.frame_izquierda, text="Copiar Palabra", command=self.copiar_palabra, state=tk.DISABLED)
        self.btn_copiar.pack(side="left", padx=5)

        self.btn_diccionario = tk.Button(self.frame_izquierda, text="Buscar Online", command=self.abrir_diccionario, state=tk.DISABLED)
        self.btn_diccionario.pack(side="left", padx=5)

        self.btn_anterior = tk.Button(self.frame_derecha, text="Anterior", command=self.palabra_anterior, state=tk.DISABLED)
        self.btn_anterior.pack(side="left", padx=5)

        self.btn_aleatorio = tk.Button(self.frame_derecha, text="Aleatorio", command=self.palabra_aleatoria, state=tk.DISABLED)
        self.btn_aleatorio.pack(side="left", padx=5)

        self.btn_siguiente = tk.Button(self.frame_derecha, text="Siguiente", command=self.palabra_siguiente, state=tk.DISABLED)
        self.btn_siguiente.pack(side="left", padx=5)

        self.btn_datos = tk.Button(self.frame_derecha, text="Editar esta palabra", command=self.mostrar_datos, state=tk.DISABLED)
        self.btn_datos.pack(side="left", padx=5)

        self.frame_central = tk.Frame(master, bg="#116eef")
        self.frame_central.pack(expand=True, fill="both")

        self.label_word = tk.Label(self.frame_central, font=("Arial", 120, "bold"), fg="white", bg="#116eef")
        self.label_word.pack(pady=(40, 10))

        self.label_ipa = tk.Label(self.frame_central, font=("Arial", 32), fg="black", bg="#116eef")
        self.label_ipa.pack(pady=(0, 10))

        self.label_transliteration = tk.Label(self.frame_central, font=("Arial", 28), fg="red", bg="#116eef")
        self.label_transliteration.pack(pady=(0, 20))

        self.label_spanish = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#116eef", wraplength=1000, justify="center")
        self.label_spanish.pack(pady=(10, 30))

        self.label_indice = tk.Label(self.frame_central, text="", font=("Arial", 16), fg="white", bg="#116eef")
        self.label_indice.pack(pady=5)

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
            for btn in [self.btn_datos, self.btn_copiar, self.btn_recargar,
                        self.btn_anterior, self.btn_aleatorio, self.btn_siguiente, self.btn_diccionario]:
                btn.config(state=tk.NORMAL)
            self.palabra_aleatoria()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")

    def recargar_json(self):
        if not self.ruta_json:
            messagebox.showwarning("Atención", "No hay archivo cargado para recargar.")
            return
        try:
            with open(self.ruta_json, "r", encoding="utf-8") as f:
                self.datos = json.load(f)
                if not isinstance(self.datos, list):
                    raise ValueError("El JSON debe contener una lista.")
            if self.indice_actual is not None and 0 <= self.indice_actual < len(self.datos):
                self.actual = self.datos[self.indice_actual]
            else:
                self.palabra_aleatoria()
            self.mostrar_palabra_actual()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo recargar el archivo:\n{e}")

    def mostrar_palabra_actual(self):
        if not self.actual:
            return
        word = self.actual.get("word", "Campo vacío")
        ipa = self.actual.get("ipa", "")
        translit = self.actual.get("transliteration", "")
        spanish = self.actual.get("spanish", "")

        self.label_word.config(text=word)
        self.label_ipa.config(text=ipa or "Sin IPA")
        self.label_transliteration.config(text=translit or "Sin transliteración")
        self.label_spanish.config(text=f"Español: {spanish}" if spanish else "Español: vacío")
        self.label_indice.config(text=f"Índice actual: {self.indice_actual + 1} / {len(self.datos)}")

    def palabra_aleatoria(self):
        if not self.datos:
            return
        self.actual = random.choice(self.datos)
        self.indice_actual = self.datos.index(self.actual)
        self.mostrar_palabra_actual()

    def palabra_siguiente(self):
        if not self.datos:
            return
        self.indice_actual = (self.indice_actual + 1) % len(self.datos)
        self.actual = self.datos[self.indice_actual]
        self.mostrar_palabra_actual()

    def palabra_anterior(self):
        if not self.datos:
            return
        self.indice_actual = (self.indice_actual - 1) % len(self.datos)
        self.actual = self.datos[self.indice_actual]
        self.mostrar_palabra_actual()

    def copiar_palabra(self):
        if self.actual and "word" in self.actual:
            self.master.clipboard_clear()
            self.master.clipboard_append(self.actual["word"])

    def abrir_diccionario(self):
        if self.actual and "word" in self.actual and self.actual["word"]:
            palabra = self.actual["word"]
            url = f"https://www.wordreference.com/definition/{palabra}"
            webbrowser.open(url)

    def mostrar_datos(self):
        if not self.actual:
            return

        orden_campos = ["word", "ipa", "transliteration",
         "spanish","english", "portuguese",
         "phrase_jp","phrase_en", "phrase_es", 
         "latin", "french", "italian", "german", "chinese", "korean","russian",
         ]

        ventana = tk.Toplevel(self.master)
        ventana.title("Editar Datos")
        ventana.configure(bg="white")
        ventana.geometry("700x400")

        canvas = tk.Canvas(ventana, bg="#116eef")
        frame_scroll = tk.Frame(canvas, bg="#116eef")
        scrollbar = tk.Scrollbar(ventana, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=frame_scroll, anchor="nw")

        entries = {}

        def on_frame_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame_scroll.bind("<Configure>", on_frame_config)

        campos_ordenados = orden_campos + [k for k in self.actual.keys() if k not in orden_campos]

        def guardar_cambios():
            for clave, entry in entries.items():
                self.actual[clave] = entry.get()
            with open(self.ruta_json, "w", encoding="utf-8") as f:
                json.dump(self.datos, f, ensure_ascii=False, indent=4)
            self.mostrar_palabra_actual()
            messagebox.showinfo("Guardado", "Cambios guardados correctamente.")
            ventana.destroy()

        btn_guardar = tk.Button(frame_scroll, text="Guardar cambios", font=("Arial", 14), command=guardar_cambios)
        btn_guardar.grid(row=0, columnspan=2, pady=20)

        for i, clave in enumerate(campos_ordenados):
            valor = self.actual.get(clave)
            tk.Label(frame_scroll, text=clave, font=("Arial", 14), bg="white").grid(row=i+1, column=0, sticky="e", padx=10, pady=5)
            entry = tk.Entry(frame_scroll, font=("Arial", 14), width=70)
            entry.grid(row=i+1, column=1, padx=10, pady=5)
            entry.insert(0, "" if valor is None else str(valor))
            entries[clave] = entry

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
