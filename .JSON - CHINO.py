import tkinter as tk
from tkinter import filedialog, messagebox
import random
import json
import webbrowser

class App:
    def __init__(self, master):
        self.master = master
        master.title("Palabras Aleatorias - Chino")
        master.configure(bg="#D0021B")
        master.state("zoomed")

        self.datos = []
        self.actual = None
        self.ruta_json = None
        self.indice_actual = None

        self.frame_botones = tk.Frame(master, bg="#D0021B")
        self.frame_botones.pack(fill="x", pady=10)

        self.frame_izquierda = tk.Frame(self.frame_botones, bg="#D0021B")
        self.frame_izquierda.pack(side="left")

        self.frame_derecha = tk.Frame(self.frame_botones, bg="#D0021B")
        self.frame_derecha.pack(side="right")

        self.btn_cargar = tk.Button(self.frame_izquierda, text="Cargar archivo JSON", command=self.cargar_archivo)
        self.btn_cargar.pack(side="left", padx=5)

        self.btn_recargar = tk.Button(self.frame_izquierda, text="Recargar JSON", command=self.recargar_json, state=tk.DISABLED)
        self.btn_recargar.pack(side="left", padx=5)

        self.btn_copiar = tk.Button(self.frame_izquierda, text="Copiar Hanzi", command=self.copiar_kanji, state=tk.DISABLED)
        self.btn_copiar.pack(side="left", padx=5)

        self.btn_diccionario = tk.Button(self.frame_izquierda, text="Diccionario", command=self.abrir_diccionario, state=tk.DISABLED)
        self.btn_diccionario.pack(side="left", padx=5)

        self.btn_anterior = tk.Button(self.frame_derecha, text="Anterior", command=self.kanji_anterior, state=tk.DISABLED)
        self.btn_anterior.pack(side="left", padx=5)

        self.btn_aleatorio = tk.Button(self.frame_derecha, text="Aleatorio", command=self.kanji_aleatorio, state=tk.DISABLED)
        self.btn_aleatorio.pack(side="left", padx=5)

        self.btn_siguiente = tk.Button(self.frame_derecha, text="Siguiente", command=self.kanji_siguiente, state=tk.DISABLED)
        self.btn_siguiente.pack(side="left", padx=5)

        self.btn_datos = tk.Button(self.frame_derecha, text="Editar esta palabra", command=self.mostrar_datos, state=tk.DISABLED)
        self.btn_datos.pack(side="left", padx=5)

        self.frame_central = tk.Frame(master, bg="#D0021B")
        self.frame_central.pack(expand=True, fill="both")

        self.label_kanji = tk.Label(self.frame_central, font=("Arial", 120, "bold"), fg="#1C1C1C", bg="#D0021B")
        self.label_kanji.pack(pady=(40, 10))

        self.label_pinyin = tk.Label(self.frame_central, font=("Arial", 32), fg="#FFD700", bg="#D0021B")
        self.label_pinyin.pack(pady=(0, 10))

        self.label_espanol = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#D0021B")
        self.label_espanol.pack()

        self.label_ingles = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#D0021B")
        self.label_ingles.pack()

        self.label_portugues = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#D0021B")
        self.label_portugues.pack()

        self.label_frances = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#D0021B")
        self.label_frances.pack()

        self.label_aleman = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#D0021B")
        self.label_aleman.pack()

        self.label_italiano = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#D0021B")
        self.label_italiano.pack()

        self.label_ruso = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#D0021B")
        self.label_ruso.pack()

        self.label_coreano = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#D0021B")
        self.label_coreano.pack()

        self.label_japones = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#D0021B")
        self.label_japones.pack()

        self.label_frase_cn = tk.Label(self.frame_central, font=("Arial", 20, "italic"), fg="white", bg="#D0021B", wraplength=900, justify="center")
        self.label_frase_cn.pack(pady=(10, 10))

        self.label_frase_es = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#D0021B", wraplength=900, justify="center")
        self.label_frase_es.pack(pady=(0, 10))

        self.label_indice = tk.Label(self.frame_central, text="", font=("Arial", 16), fg="white", bg="#D0021B")
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
            self.btn_datos.config(state=tk.NORMAL)
            self.btn_copiar.config(state=tk.NORMAL)
            self.btn_recargar.config(state=tk.NORMAL)
            self.btn_anterior.config(state=tk.NORMAL)
            self.btn_aleatorio.config(state=tk.NORMAL)
            self.btn_siguiente.config(state=tk.NORMAL)
            self.btn_diccionario.config(state=tk.NORMAL)
            self.kanji_aleatorio()
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
                self.kanji_aleatorio()
            self.mostrar_palabra_actual()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo recargar el archivo:\n{e}")

    def mostrar_palabra_actual(self):
        if not self.actual:
            return
        hanzi = self.actual.get("hanzi_s")
        pinyin = self.actual.get("pinyin")
        espanol = self.actual.get("spanish")
        ingles = self.actual.get("english")
        portugues = self.actual.get("portuguese")
        frances = self.actual.get("french")
        aleman = self.actual.get("german")
        italiano = self.actual.get("italian")
        ruso = self.actual.get("russian")
        coreano = self.actual.get("korean")
        japones = self.actual.get("japanese")
        frase_cn = self.actual.get("phrase_cn_s")
        frase_es = self.actual.get("phrase_es")

        self.label_kanji.config(text=hanzi or "Campo vacío")
        self.label_pinyin.config(text=pinyin or "Sin pinyin")
        self.label_espanol.config(text=f"Español: {espanol}" if espanol else "Español: vacío")
        self.label_ingles.config(text=f"Inglés: {ingles}" if ingles else "Inglés: vacío")
        self.label_portugues.config(text=f"Portugués: {portugues}" if portugues else "Portugués: vacío")
        self.label_frances.config(text=f"Francés: {frances}" if frances else "Francés: vacío")
        self.label_aleman.config(text=f"Alemán: {aleman}" if aleman else "Alemán: vacío")
        self.label_italiano.config(text=f"Italiano: {italiano}" if italiano else "Italiano: vacío")
        self.label_ruso.config(text=f"Ruso: {ruso}" if ruso else "Ruso: vacío")
        self.label_coreano.config(text=f"Coreano: {coreano}" if coreano else "Coreano: vacío")
        self.label_japones.config(text=f"Japonés: {japones}" if japones else "Japonés: vacío")
        self.label_frase_cn.config(text=frase_cn or "")
        self.label_frase_es.config(text=frase_es or "")
        self.label_indice.config(text=f"Índice actual: {self.indice_actual + 1} / {len(self.datos)}")

    def kanji_aleatorio(self):
        if not self.datos:
            return
        self.actual = random.choice(self.datos)
        self.indice_actual = self.datos.index(self.actual)
        self.mostrar_palabra_actual()

    def kanji_siguiente(self):
        if not self.datos:
            return
        self.indice_actual = (self.indice_actual + 1) % len(self.datos)
        self.actual = self.datos[self.indice_actual]
        self.mostrar_palabra_actual()

    def kanji_anterior(self):
        if not self.datos:
            return
        self.indice_actual = (self.indice_actual - 1) % len(self.datos)
        self.actual = self.datos[self.indice_actual]
        self.mostrar_palabra_actual()

    def copiar_kanji(self):
        if self.actual and "hanzi_s" in self.actual:
            self.master.clipboard_clear()
            self.master.clipboard_append(self.actual["hanzi_s"])

    def abrir_diccionario(self):
        if self.actual and "hanzi_s" in self.actual and self.actual["hanzi_s"]:
            hanzi = self.actual["hanzi_s"]
            url = f"https://www.mdbg.net/chinese/dictionary?page=worddict&wdqb={hanzi}"
            webbrowser.open(url)

    def mostrar_datos(self):
        if not self.actual:
            return

        orden_campos = [
            "hanzi_s", "hanzi_t", "pinyin", "ipa",
            "phrase_cn_s", "phrase_es",
            "spanish", "english", "portuguese",
            "latin", "french", "german", "italian",
            "japanese", "korean", "russian","hindi", 
        ]

        ventana = tk.Toplevel(self.master)
        ventana.title("Editar Datos")
        ventana.configure(bg="white")
        ventana.geometry("800x600")

        canvas = tk.Canvas(ventana, bg="#D0021B")
        frame_scroll = tk.Frame(canvas, bg="#D0021B")
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
            entry = tk.Entry(frame_scroll, font=("Arial", 14), width=90)
            entry.grid(row=i+1, column=1, padx=10, pady=5)
            entry.insert(0, "" if valor is None else str(valor))
            entries[clave] = entry

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
