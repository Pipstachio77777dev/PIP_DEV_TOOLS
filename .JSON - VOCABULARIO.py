import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import random
import json
import webbrowser

class App:
    def __init__(self, master):
        self.master = master
        master.title("Vocabulario - Japonés")
        master.configure(bg="#dde8ea")
        try:
            master.state("zoomed")
        except Exception:
            pass

        self.datos = []
        self.actual = None
        self.ruta_json = None
        self.indice_actual = None
        self.ventana_edicion = None
        self.ventana_agregar = None
        self.ventana_json = None  # Inicializa la referencia a la ventana de edición JSON


        # --- Frames y botones ---
        self.frame_botones = tk.Frame(master, bg="#dde8ea")
        self.frame_botones.pack(fill="x", pady=10)

        self.frame_izquierda = tk.Frame(self.frame_botones, bg="#dde8ea")
        self.frame_izquierda.pack(side="left")
        self.frame_derecha = tk.Frame(self.frame_botones, bg="#dde8ea")
        self.frame_derecha.pack(side="right")

        # --- Botones izquierda (2 filas) ---
        self.btn_cargar = tk.Button(self.frame_izquierda, text="Cargar JSON 📄", command=self.cargar_archivo,
                                    bg="#639697", fg="white", font=("Arial", 12, "bold"))
        self.btn_cargar.grid(row=0, column=0, padx=5, pady=5)
        self.btn_recargar = tk.Button(self.frame_izquierda, text="Recargar JSON 🔄", command=self.recargar_json,
                                      state=tk.DISABLED, bg="#639697", fg="white", font=("Arial", 12, "bold"))
        self.btn_recargar.grid(row=0, column=1, padx=5, pady=5)


        self.btn_diccionario = tk.Button(self.frame_izquierda, text="Diccionario", command=self.abrir_diccionario,
                                        state=tk.DISABLED, bg="#066006", fg="white", font=("Arial", 12, "bold"))
        self.btn_diccionario.grid(row=0, column=2, padx=5, pady=5)

        self.btn_copiar = tk.Button(self.frame_izquierda, text="Copiar", command=self.copiar_kanji, state=tk.DISABLED,
                                    bg="#062c60", fg="white", font=("Arial", 12, "bold"))
        self.btn_copiar.grid(row=1, column=0, padx=5, pady=5)




        self.btn_editar_json = tk.Button(
            self.frame_izquierda,
            text="Editar Bloque 📝",
            command=self.editar_json,
            state=tk.DISABLED,
            bg="#062c60", fg="white", font=("Arial", 12, "bold")
        )
        self.btn_editar_json.grid(row=1, column=2, padx=5, pady=5)

        



        

        self.btn_datos = tk.Button(self.frame_izquierda, text="Editar campos ⚙️", command=self.mostrar_datos, state=tk.DISABLED,
                                   bg="#062c60", fg="white", font=("Arial", 12, "bold"))
        self.btn_datos.grid(row=1, column=1, padx=5, pady=5)




        # --- Botones derecha (2 filas) ---
        self.btn_anterior = tk.Button(self.frame_derecha, text="anterior", command=self.kanji_anterior, state=tk.DISABLED, bg="#116eef", fg="white", font=("Arial", 12, "bold"))
        self.btn_anterior.grid(row=0, column=0, padx=5, pady=5)


        self.btn_siguiente = tk.Button(self.frame_derecha, text="siguiente", command=self.kanji_siguiente,  state=tk.DISABLED, bg="#116eef", fg="white", font=("Arial", 12, "bold"))
        self.btn_siguiente.grid(row=0, column=1, padx=5, pady=5)

        self.btn_aleatorio = tk.Button(self.frame_derecha, text="aleatorio", command=self.kanji_aleatorio, state=tk.DISABLED, bg="#116eef", fg="white", font=("Arial", 12, "bold"))
        self.btn_aleatorio.grid(row=0, column=2, padx=5, pady=5)


        self.btn_buscar = tk.Button(self.frame_derecha, text="Buscar 🔍", command=self.buscar_palabra, state=tk.DISABLED,  bg="#116eef", fg="white", font=("Arial", 12, "bold"))
        self.btn_buscar.grid(row=0, column=3, padx=5, pady=5)






        self.btn_agregar = tk.Button(self.frame_derecha, text="Agregar", command=self.agregar_palabra,
                                     bg="#603306", fg="white", font=("Arial", 12, "bold"))
        self.btn_agregar.grid(row=2, column=3, padx=5, pady=5)

        self.btn_minimo = tk.Button(self.frame_derecha, text="Vacio ⚠️", command=self.mostrar_minimo_funcional,
                                    state=tk.DISABLED, bg="#ef1010", fg="white", font=("Arial", 12, "bold"))
        self.btn_minimo.grid(row=2, column=0, padx=5, pady=5)

        self.btn_corchetes = tk.Button(self.frame_derecha, text="Ir a  [ ] ⚠️", command=self.detectar_corchetes,
                                       state=tk.DISABLED, bg="#eeef10", fg="black", font=("Arial", 12, "bold"))
        self.btn_corchetes.grid(row=2, column=1, padx=5, pady=5)

        self.btn_touten = tk.Button(self.frame_derecha, text="Ir a 、⚠️", command=self.detectar_touten,
                                    state=tk.DISABLED, bg="#eeef10", fg="black", font=("Arial", 12, "bold"))
        self.btn_touten.grid(row=2, column=2, padx=5, pady=5)

        

        # --- Frame central ---
        self.frame_central = tk.Frame(master, bg="#dde8ea")
        self.frame_central.pack(expand=True, fill="both")

        self.label_indice = tk.Label(self.frame_central, text="", font=("Arial", 16), fg="#116eef", bg="#dde8ea")
        self.label_indice.pack(pady=5)
        self.label_furigana = tk.Label(self.frame_central, font=("Arial", 32), fg="white", bg="#dde8ea")
        self.label_furigana.pack(pady=(10, 10))
        self.label_kanji = tk.Label(self.frame_central, font=("Arial", 120, "bold"), fg="white", bg="#dde8ea")
        self.label_kanji.pack(pady=(0, 10))
        self.label_romaji = tk.Label(self.frame_central, font=("Arial", 28), fg="white", bg="#dde8ea")
        self.label_romaji.pack(pady=(0, 20))
        self.label_espanol = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#dde8ea")
        self.label_espanol.pack()
        self.label_ingles = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#dde8ea")
        self.label_ingles.pack()
        self.label_portuguese = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#dde8ea")
        self.label_portuguese.pack()
        self.label_frase_jp = tk.Label(self.frame_central, font=("Arial", 20, "italic"), fg="white", bg="#dde8ea",
                                       wraplength=900, justify="center")
        self.label_frase_jp.pack(pady=(10, 10))
        self.label_frase_es = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#dde8ea",
                                       wraplength=900, justify="center")
        self.label_frase_es.pack(pady=(0, 10))
        self.label_frase_en = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#dde8ea",
                                       wraplength=900, justify="center")
        self.label_frase_en.pack(pady=(0, 30))

    # --- Funciones de búsqueda ---
    def buscar_palabra(self):
        if not self.datos:
            messagebox.showwarning("Atención", "No hay datos cargados.")
            return

        termino = simpledialog.askstring("Buscar palabra", "Ingrese texto o kanji a buscar:")
        if not termino:
            return
        termino = termino.strip().lower()

        coincidencias = []
        for i, item in enumerate(self.datos):
            for valor in item.values():
                if isinstance(valor, str) and termino in valor.lower():
                    coincidencias.append(i)
                    break

        if not coincidencias:
            messagebox.showinfo("Sin resultados", f"No se encontró ninguna coincidencia con: '{termino}'")
            return

        ventana_resultados = tk.Toplevel(self.master)
        ventana_resultados.title(f"Resultados de búsqueda: '{termino}'")
        ventana_resultados.geometry("500x300")
        ventana_resultados.configure(bg="#dde8ea")

        indice_actual = tk.IntVar(value=0)

        lbl_info = tk.Label(
            ventana_resultados,
            text="",
            font=("Arial", 14),
            bg="#dde8ea",
            fg="#639697",
            wraplength=460,
            justify="center"
        )
        lbl_info.pack(pady=20)

        frame_botones = tk.Frame(ventana_resultados, bg="#dde8ea")
        frame_botones.pack(pady=10)

        btn_anterior = tk.Button(frame_botones, text="← Anterior", bg="#639697", fg="white",
                                 font=("Arial", 12, "bold"))
        btn_anterior.pack(side="left", padx=10)

        btn_siguiente = tk.Button(frame_botones, text="Siguiente →", bg="#639697", fg="white",
                                  font=("Arial", 12, "bold"))
        btn_siguiente.pack(side="left", padx=10)

        def mostrar_actual():
            idx = coincidencias[indice_actual.get()]
            item = self.datos[idx]
            campos = [
                f"Índice: {idx + 1}/{len(self.datos)}",
                f"Kanji: {item.get('kanji', '')}",
                f"Furigana: {item.get('furigana', '')}",
                f"Romaji: {item.get('romaji', '')}",
                f"Español: {item.get('spanish', '')}",
                f"Inglés: {item.get('english', '')}",
            ]
            lbl_info.config(
                text=f"Coincidencia {indice_actual.get() + 1} de {len(coincidencias)}\n\n" +
                     "\n".join(campos)
            )
            self.actual = item
            self.indice_actual = idx
            self.mostrar_palabra_actual()

        def siguiente():
            indice_actual.set((indice_actual.get() + 1) % len(coincidencias))
            mostrar_actual()

        def anterior():
            indice_actual.set((indice_actual.get() - 1) % len(coincidencias))
            mostrar_actual()

        btn_anterior.config(command=anterior)
        btn_siguiente.config(command=siguiente)

        mostrar_actual()

    # --- Funciones principales ---
    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")])
        if not ruta:
            return
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
                if not isinstance(datos, list):
                    raise ValueError("El JSON debe contener una lista.")
                self.datos = datos
            self.ruta_json = ruta
            for btn in [self.btn_datos, self.btn_copiar, self.btn_recargar, self.btn_anterior, self.btn_aleatorio,
                        self.btn_siguiente, self.btn_diccionario, self.btn_minimo, self.btn_agregar, self.btn_corchetes,
                        self.btn_touten, self.btn_buscar, self.btn_editar_json]:
                btn.config(state=tk.NORMAL)
            if self.datos:
                self.kanji_aleatorio()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")

    def recargar_json(self):
        if not self.ruta_json:
            messagebox.showwarning("Atención", "No hay archivo cargado para recargar.")
            return
        try:
            with open(self.ruta_json, "r", encoding="utf-8") as f:
                datos = json.load(f)
                if not isinstance(datos, list):
                    raise ValueError("El JSON debe contener una lista.")
                self.datos = datos
            if self.indice_actual is not None and 0 <= self.indice_actual < len(self.datos):
                self.actual = self.datos[self.indice_actual]
            elif self.datos:
                self.kanji_aleatorio()
            else:
                self.actual = None
                self.indice_actual = None
            self.mostrar_palabra_actual()
            self.btn_editar_json.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo recargar el archivo:\n{e}")

    # --- Mostrar palabra actual ---
    def mostrar_palabra_actual(self):
        if not self.actual:
            for label in [self.label_kanji, self.label_furigana, self.label_romaji, self.label_espanol, self.label_ingles,
                          self.label_portuguese, self.label_frase_jp, self.label_frase_es, self.label_frase_en]:
                try:
                    label.config(text="", fg="white", bg="#f2f7fd")
                except Exception:
                    pass
            self.label_indice.config(text="")
            return

        campos_mostrar = {
            "kanji": (self.label_kanji, "#Campo vacio#"),
            "furigana": (self.label_furigana, "#no hay furigana#"),
            "romaji": (self.label_romaji, "#no hay romaji#"),
            "spanish": (self.label_espanol, "###Español: Campo vacio###", "Español: "),
            "english": (self.label_ingles, "###Inglés: Campo vacio###", "Inglés: "),
            "portuguese": (self.label_portuguese, "#Portugues: campo vacio#", "Portugues: "),
            "phrase_jp": (self.label_frase_jp, "#falta ejemplo en japones#"),
            "phrase_es": (self.label_frase_es, "#Falta frase en español#"),
            "phrase_en": (self.label_frase_en, "#Falta frase en inglés#")
        }

        for clave, datos in campos_mostrar.items():
            label = datos[0]
            valor = self.actual.get(clave)
            texto = valor if valor else datos[1]
            if len(datos) == 3:
                texto = f"{datos[2]}{valor}" if valor else datos[1]

            if clave == "kanji":
                if valor:
                    label.config(text=texto, fg="white", bg="#116eef")
                else:
                    label.config(text=texto, fg="red", bg="#dde8ea")
            else:
                label.config(text=texto, fg="grey" if valor else "red", bg="#dde8ea")

        try:
            if self.indice_actual is None:
                idx_text = f"Índice actual: ? / {len(self.datos)}"
            else:
                idx_text = f"Índice actual: {self.indice_actual + 1} / {len(self.datos)}"
            self.label_indice.config(text=idx_text)
        except Exception:
            self.label_indice.config(text="")

    # --- Navegación ---
    def kanji_anterior(self):
        if not self.datos:
            return
        if self.indice_actual is None:
            self.indice_actual = 0
        self.indice_actual = (self.indice_actual - 1) % len(self.datos)
        self.actual = self.datos[self.indice_actual]
        self.mostrar_palabra_actual()

    def kanji_aleatorio(self):
        if not self.datos:
            return
        self.actual = random.choice(self.datos)
        try:
            self.indice_actual = self.datos.index(self.actual)
        except ValueError:
            self.indice_actual = 0
            self.actual = self.datos[0]
        self.mostrar_palabra_actual()

    def kanji_siguiente(self):
        if not self.datos:
            return
        if self.indice_actual is None:
            self.indice_actual = 0
        self.indice_actual = (self.indice_actual + 1) % len(self.datos)
        self.actual = self.datos[self.indice_actual]
        self.mostrar_palabra_actual()

    # --- Copiar kanji ---
    def copiar_kanji(self):
        if self.actual and "kanji" in self.actual and self.actual.get("kanji"):
            try:
                self.master.clipboard_clear()
                self.master.clipboard_append(self.actual["kanji"])
            except Exception:
                pass

    # --- Abrir diccionario ---
    def abrir_diccionario(self):
        if self.actual and "kanji" in self.actual and self.actual["kanji"]:
            kanji = self.actual["kanji"]
            url = f"https://jisho.org/search/{kanji}"
            try:
                webbrowser.open(url)
            except Exception:
                pass

    # --- Detectar corchetes y touten ---
    def detectar_corchetes(self):
        for i, item in enumerate(self.datos):
            for valor in item.values():
                if isinstance(valor, str) and ("[" in valor or "]" in valor):
                    self.actual = item
                    self.indice_actual = i
                    self.mostrar_palabra_actual()
                    return
        messagebox.showinfo("Sin resultados", "No se encontró ningún campo con corchetes [ o ].")

    def detectar_touten(self):
        for i, item in enumerate(self.datos):
            for valor in item.values():
                if isinstance(valor, str) and "、" in valor:
                    self.actual = item
                    self.indice_actual = i
                    self.mostrar_palabra_actual()
                    return
        messagebox.showinfo("Sin resultados", "No se encontró ningún campo.")

    def mostrar_minimo_funcional(self):
        campos = ["furigana", "spanish", "romaji", "english"]
        for i, item in enumerate(self.datos):
            if any(item.get(campo) in [None, ""] for campo in campos):
                self.actual = item
                self.indice_actual = i
                self.mostrar_palabra_actual()
                return
        messagebox.showinfo("Completos", "Todos los registros tienen los campos mínimos llenos.")

    # --- Agregar palabra ---
    def agregar_palabra(self):
        if self.ventana_agregar is not None and self.ventana_agregar.winfo_exists():
            self.ventana_agregar.lift()
            return
        self.ventana_agregar = tk.Toplevel(self.master)
        self.ventana_agregar.title("Agregar Nueva Palabra")
        self.ventana_agregar.configure(bg="black")
        self.ventana_agregar.geometry("600x400")

        campos = ["kanji", "furigana", "romaji", "spanish", "english", "portuguese","phrase_jp",  "phrase_es", "phrase_en",
                  "latin","french","italian","german","chinese","korean","russian"]
        entries = {}
        for i, campo in enumerate(campos):
            tk.Label(self.ventana_agregar, text=campo, font=("Arial", 12, "bold"), bg="black", fg="#f0c75e").grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(self.ventana_agregar, font=("Arial", 12), width=40)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[campo] = entry

        def guardar_nueva():
            nueva_palabra = {campo: entries[campo].get().strip() for campo in campos}
            if not nueva_palabra["kanji"]:
                messagebox.showwarning("Error", "El campo 'kanji' es obligatorio.")
                return
            for item in self.datos:
                if item.get("kanji") == nueva_palabra["kanji"]:
                    messagebox.showerror("Error", f"La palabra con kanji '{nueva_palabra['kanji']}' ya existe.")
                    return
            self.datos.append(nueva_palabra)

            try:
                if not self.ruta_json:
                    guardar_ruta = filedialog.asksaveasfilename(defaultextension=".json",
                                                                filetypes=[("Archivos JSON", "*.json")],
                                                                title="Guardar JSON")
                    if not guardar_ruta:
                        self.datos.pop()
                        messagebox.showinfo("Cancelado", "No se guardó la nueva palabra (no se eligió archivo).")
                        return
                    self.ruta_json = guardar_ruta
                with open(self.ruta_json, "w", encoding="utf-8") as f:
                    json.dump(self.datos, f, ensure_ascii=False, indent=4)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo JSON:\n{e}")
                if self.datos and self.datos[-1] == nueva_palabra:
                    self.datos.pop()
                return

            messagebox.showinfo("Éxito", "Palabra agregada correctamente.")
            self.ventana_agregar.destroy()
            self.ventana_agregar = None
            self.actual = nueva_palabra
            self.indice_actual = len(self.datos) - 1
            self.mostrar_palabra_actual()
            for btn in [self.btn_datos, self.btn_copiar, self.btn_recargar, self.btn_anterior, self.btn_aleatorio,
                        self.btn_siguiente, self.btn_diccionario, self.btn_minimo, self.btn_agregar, self.btn_corchetes,
                        self.btn_touten, self.btn_buscar, self.btn_editar_json]:
                btn.config(state=tk.NORMAL)

        btn_guardar = tk.Button(self.ventana_agregar, text="Guardar palabra", font=("Arial", 12, "bold"), bg="#66bb6a", fg="black", command=guardar_nueva)
        btn_guardar.grid(row=len(campos), column=0, columnspan=2, pady=20)
        self.ventana_agregar.protocol("WM_DELETE_WINDOW", lambda: [self.ventana_agregar.destroy(), setattr(self, 'ventana_agregar', None)])

    # --- Editar palabra ---
    def mostrar_datos(self):
        if self.ventana_edicion is not None and self.ventana_edicion.winfo_exists():
            self.ventana_edicion.lift()
            return
        if not self.actual:
            return

        orden_campos = [
            "kanji", "furigana", "romaji","spanish","english", "portuguese",
            "phrase_jp","phrase_es","phrase_en",
            "latin","french","italian","german","chinese","korean","russian",
        ]

        self.ventana_edicion = tk.Toplevel(self.master)
        self.ventana_edicion.title("Editar Datos")
        self.ventana_edicion.configure(bg="black")
        self.ventana_edicion.geometry("900x800")

        canvas = tk.Canvas(self.ventana_edicion, bg="black")
        frame_scroll = tk.Frame(canvas, bg="black")
        scrollbar = tk.Scrollbar(self.ventana_edicion, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=frame_scroll, anchor="nw")

        entries = {}
        frame_scroll.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        campos_ordenados = orden_campos + [k for k in self.actual.keys() if k not in orden_campos]

        def guardar_cambios():
            for clave, entry in entries.items():
                self.actual[clave] = entry.get()
            try:
                if not self.ruta_json:
                    guardar_ruta = filedialog.asksaveasfilename(defaultextension=".json",
                                                                filetypes=[("Archivos JSON", "*.json")],
                                                                title="Guardar JSON")
                    if not guardar_ruta:
                        messagebox.showwarning("Atención", "No se guardaron los cambios (no se eligió archivo).")
                        return
                    self.ruta_json = guardar_ruta
                with open(self.ruta_json, "w", encoding="utf-8") as f:
                    json.dump(self.datos, f, ensure_ascii=False, indent=4)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo JSON:\n{e}")
                return
            self.mostrar_palabra_actual()
            messagebox.showinfo("Guardado", "Cambios guardados correctamente.")
            self.ventana_edicion.destroy()
            self.ventana_edicion = None

        def eliminar_palabra():
            if messagebox.askyesno("Eliminar", "¿Estás seguro de que quieres eliminar esta palabra?"):
                if self.indice_actual is None or not (0 <= self.indice_actual < len(self.datos)):
                    messagebox.showerror("Error", "Índice inválido, no se puede eliminar.")
                    return
                self.datos.pop(self.indice_actual)
                try:
                    if self.ruta_json:
                        with open(self.ruta_json, "w", encoding="utf-8") as f:
                            json.dump(self.datos, f, ensure_ascii=False, indent=4)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo actualizar el archivo JSON:\n{e}")
                self.ventana_edicion.destroy()
                self.ventana_edicion = None
                if self.datos:
                    self.indice_actual = min(self.indice_actual, len(self.datos) - 1)
                    self.actual = self.datos[self.indice_actual]
                    self.mostrar_palabra_actual()
                else:
                    self.actual = None
                    self.indice_actual = None
                    for label in [self.label_kanji, self.label_furigana, self.label_romaji,
                                  self.label_espanol, self.label_ingles, self.label_portuguese,
                                  self.label_frase_jp, self.label_frase_es, self.label_frase_en]:
                        label.config(text="", fg="white", bg="#f2f7fd")
                    self.label_indice.config(text="")
                messagebox.showinfo("Eliminado", "Palabra eliminada correctamente.")

        btn_frame = tk.Frame(frame_scroll, bg="black")
        btn_frame.grid(row=0, column=0, columnspan=2, pady=10)

        tk.Button(btn_frame, text="Guardar cambios", font=("Arial", 14, "bold"), bg="black", fg="#f0c75e",
                  command=guardar_cambios).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Eliminar palabra", font=("Arial", 14, "bold"), bg="black", fg="red",
                  command=eliminar_palabra).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Copiar Kanji 📋", font=("Arial", 14, "bold"), bg="black", fg="#f0c75e",
                  command=self.copiar_kanji).pack(side="left", padx=10)

        for i, clave in enumerate(campos_ordenados):
            valor = self.actual.get(clave)
            tk.Label(frame_scroll, text=clave, font=("Arial", 14, "bold"), bg="black", fg="#f0c75e").grid(row=i+1, column=0, sticky="e", padx=10, pady=5)
            entry = tk.Entry(frame_scroll, font=("Arial", 14), width=99)
            entry.grid(row=i+1, column=1, padx=10, pady=5)
            entry.insert(0, "" if valor is None else str(valor))
            entries[clave] = entry

        self.ventana_edicion.protocol("WM_DELETE_WINDOW", lambda: [self.ventana_edicion.destroy(), setattr(self, 'ventana_edicion', None)])

    # --- Editar JSON completo ---
        # --- Editar solo el bloque JSON del kanji actual ---
        # --- Editar JSON completo ---
    # --- Editar solo el bloque JSON del kanji actual ---
    def editar_json(self):
        if not self.datos or not self.actual:
            messagebox.showwarning("Atención", "No hay palabra seleccionada para editar.")
            return

        # Evitar abrir dos ventanas
        if self.ventana_json and self.ventana_json.winfo_exists():
            self.ventana_json.lift()  # Traer al frente si ya existe
            return

        self.ventana_json = tk.Toplevel(self.master)
        self.ventana_json.title(f"Editar JSON: {self.actual.get('kanji', '(sin kanji)')}")
        self.ventana_json.geometry("700x600")
        self.ventana_json.configure(bg="#dde8ea")

        # Mostrar solo el bloque de la palabra actual
        text_area = tk.Text(self.ventana_json, font=("Courier", 12), wrap="none")
        text_area.pack(fill="both", expand=True, padx=10, pady=10)
        text_area.insert("1.0", json.dumps(self.actual, ensure_ascii=False, indent=4))

        # Barras de desplazamiento
        scroll_y = tk.Scrollbar(text_area, orient="vertical", command=text_area.yview)
        scroll_y.pack(side="right", fill="y")
        text_area.configure(yscrollcommand=scroll_y.set)

        scroll_x = tk.Scrollbar(text_area, orient="horizontal", command=text_area.xview)
        scroll_x.pack(side="bottom", fill="x")
        text_area.configure(xscrollcommand=scroll_x.set)

        def guardar_json():
            try:
                nuevo_obj = json.loads(text_area.get("1.0", tk.END))
                if not isinstance(nuevo_obj, dict):
                    messagebox.showerror("Error", "Debe ser un objeto JSON (una palabra entre {}).")
                    return

                # Reemplazar el objeto actual por el nuevo
                if self.indice_actual is not None and 0 <= self.indice_actual < len(self.datos):
                    self.datos[self.indice_actual] = nuevo_obj
                else:
                    messagebox.showerror("Error", "No se encontró el índice de la palabra actual.")
                    return

                # Guardar en el archivo
                if self.ruta_json:
                    with open(self.ruta_json, "w", encoding="utf-8") as f:
                        json.dump(self.datos, f, ensure_ascii=False, indent=4)

                self.actual = nuevo_obj
                self.mostrar_palabra_actual()
                messagebox.showinfo("Guardado", "Palabra actual actualizada correctamente.")
                self.ventana_json.destroy()
                self.ventana_json = None  # Limpiar referencia

            except json.JSONDecodeError as e:
                messagebox.showerror("Error de JSON", f"Formato JSON inválido:\n{e}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el JSON:\n{e}")

        btn_guardar = tk.Button(
            self.ventana_json,
            text="Guardar cambios",
            font=("Arial", 12, "bold"),
            bg="#66bb6a",
            fg="black",
            command=guardar_json
        )
        btn_guardar.pack(pady=10)

        # Manejar cierre de la ventana con la X
        self.ventana_json.protocol("WM_DELETE_WINDOW", lambda: [self.ventana_json.destroy(), setattr(self, 'ventana_json', None)])



if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)

    root.bind("<Control-q>", lambda event: app.mostrar_minimo_funcional())


    root.bind("<Control-w>", lambda event: app.editar_json())


    root.bind("<Control-e>", lambda event: app.mostrar_datos())



    root.bind("<Right>", lambda event: app.kanji_siguiente())
    root.bind("<Left>", lambda event: app.kanji_anterior())




    # Flechas arriba/abajo para kanji aleatorio
    root.bind("<Up>", lambda event: app.kanji_aleatorio())
    root.bind("<Down>", lambda event: app.kanji_aleatorio())





    root.mainloop()
