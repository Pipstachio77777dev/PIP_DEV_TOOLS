import tkinter as tk
from tkinter import filedialog, messagebox
import random
import json
import webbrowser
import os


class App:
    def __init__(self, master):
        self.master = master
        master.title("Palabras Aleatorias - Japonés")
        master.configure(bg="#f2f7fd")
        try:
            master.state("zoomed")
        except:
            pass

        self.datos = []
        self.actual = None
        self.ruta_json = None
        self.indice_actual = None
        self.ventana_edicion = None
        self.resultados_busqueda = []
        self.indice_resultado = 0
        self.ventana_busqueda = None

        # --- Crear menú ---
        self.crear_menu()

        # --- Panel central ---
        self.frame_central = tk.Frame(master, bg="#f2f7fd")
        self.frame_central.pack(expand=True, fill="both")

        self.label_indice = tk.Label(self.frame_central, text="", font=("Arial", 16), fg="#116eef", bg="#f2f7fd")
        self.label_indice.pack(pady=5)

        self.label_kanji = tk.Label(self.frame_central, font=("Arial", 120, "bold"), fg="white", bg="#116eef")
        self.label_kanji.pack(pady=(40, 10))

        self.label_pinyin = tk.Label(self.frame_central, font=("Arial", 32), fg="white", bg="#f2f7fd")
        self.label_pinyin.pack(pady=(0, 10))

        self.label_onyomi = tk.Label(self.frame_central, font=("Arial", 24), fg="white", bg="#f2f7fd")
        self.label_onyomi.pack(pady=(0, 10))

        self.label_on_romaji = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#f2f7fd")
        self.label_on_romaji.pack(pady=(0, 10))

        self.label_kunyomi = tk.Label(self.frame_central, font=("Arial", 24), fg="white", bg="#f2f7fd")
        self.label_kunyomi.pack(pady=(0, 10))

        self.label_kun_romaji = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#f2f7fd")
        self.label_kun_romaji.pack(pady=(0, 10))

        self.label_espanol = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#f2f7fd")
        self.label_espanol.pack()

        self.label_ingles = tk.Label(self.frame_central, font=("Arial", 20), fg="white", bg="#f2f7fd")
        self.label_ingles.pack()

        # contenedor dinámico para tabla de ejemplos
        self.frame_example = tk.Frame(self.frame_central, bg="#000000")
        self.frame_example.pack(pady=(10, 30))
        self.table_examples = None

        # Mapeo para nombres legibles
        self.display_names = {
            "kanji": "Kanji",
            "spanish": "Spanish",
            "english": "English",
            "pinyin": "Pinyin",
            "onyomi": "Onyomi",
            "on_romaji": "On Romaji",
            "kunyomi": "Kunyomi",
            "kun_romaji": "Kun Romaji",
            "example": "Example",
            "example_kana": "Example furigana",
            "example_ro": "Example (Ro)",
            "example_es": "Example (ES)",
            "example_en": "Example (EN)"
        }

    # ---------------------- Crear menú ----------------------
    def crear_menu(self):
        menubar = tk.Menu(self.master)

        # Menú Archivo
        self.menu_archivo = tk.Menu(menubar, tearoff=0)
        self.menu_archivo.add_command(label="Cargar archivo JSON", command=self.cargar_archivo)
        self.menu_archivo.add_command(label="Recargar JSON", command=self.recargar_json, state=tk.DISABLED)
        self.menu_archivo.add_separator()
        self.menu_archivo.add_command(label="Salir", command=self.master.quit)
        menubar.add_cascade(label="Archivo", menu=self.menu_archivo)

        # Menú Edición
        self.menu_edicion = tk.Menu(menubar, tearoff=0)
        self.menu_edicion.add_command(label="Editar esta palabra", command=self.mostrar_datos, state=tk.DISABLED)
        self.menu_edicion.add_command(label="Editar JSON", command=self.editar_json_actual, state=tk.DISABLED)
        menubar.add_cascade(label="Edición", menu=self.menu_edicion)

        # Menú Navegación
        self.menu_navegacion = tk.Menu(menubar, tearoff=0)
        self.menu_navegacion.add_command(label="Kanji anterior", command=self.kanji_anterior, state=tk.DISABLED)
        self.menu_navegacion.add_command(label="Kanji aleatorio", command=self.kanji_aleatorio, state=tk.DISABLED)
        self.menu_navegacion.add_command(label="Kanji siguiente", command=self.kanji_siguiente, state=tk.DISABLED)
        menubar.add_cascade(label="Navegación", menu=self.menu_navegacion)

        # Menú Herramientas
        self.menu_herramientas = tk.Menu(menubar, tearoff=0)
        self.menu_herramientas.add_command(label="Copiar Kanji", command=self.copiar_kanji, state=tk.DISABLED)
        self.menu_herramientas.add_command(label="Diccionario", command=self.abrir_diccionario, state=tk.DISABLED)
        self.menu_herramientas.add_separator()
        self.menu_herramientas.add_command(label="Ir al campo vacío", command=self.ir_campo_vacio, state=tk.DISABLED)
        self.menu_herramientas.add_command(label="Ir a example largo", command=self.ir_example_largo, state=tk.DISABLED)
        self.menu_herramientas.add_command(label="Ir a [ ]", command=self.detectar_corchetes, state=tk.DISABLED)
        self.menu_herramientas.add_command(label="Ir a , y .", command=self.detectar_corchetes1, state=tk.DISABLED)
        self.menu_herramientas.add_separator()
        self.menu_herramientas.add_command(label="Buscar", command=self.abrir_busqueda, state=tk.DISABLED)
        menubar.add_cascade(label="Herramientas", menu=self.menu_herramientas)

        self.master.config(menu=menubar)

    def _enable_menu_items_safe(self, menu):
        """Habilita todas las entradas de un menú, ignorando separadores y errores de index."""
        try:
            end = menu.index("end")
        except tk.TclError:
            end = None
        if end is None:
            return
        for i in range(end + 1):
            try:
                menu.entryconfig(i, state=tk.NORMAL)
            except tk.TclError:
                # Algunos índices pueden corresponder a separadores u otros items no configurables
                pass

    # ---------------------- Archivo ----------------------
    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")])
        if not ruta:
            return
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
            if not isinstance(datos, list):
                raise ValueError("El JSON debe contener una lista de objetos.")
            self.datos = datos
            self.ruta_json = ruta
            nombre_archivo = os.path.basename(ruta)
            self.master.title(f"[{nombre_archivo}] Palabras Aleatorias - Japonés")

            # Activar opciones del menú de forma segura
            for menu in [self.menu_edicion, self.menu_navegacion, self.menu_herramientas]:
                self._enable_menu_items_safe(menu)
            # Habilitar "Recargar JSON" en Archivo (índice 1 tal como lo añadimos)
            try:
                self.menu_archivo.entryconfig(1, state=tk.NORMAL)
            except tk.TclError:
                # si por alguna razón no funciona por índice, tratamos por label (tolerante)
                try:
                    self.menu_archivo.entryconfig("Recargar JSON", state=tk.NORMAL)
                except Exception:
                    pass

            # Mostrar un kanji aleatorio
            self.kanji_aleatorio()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")

    def recargar_json(self):
        if not self.ruta_json:
            return
        try:
            with open(self.ruta_json, "r", encoding="utf-8") as f:
                self.datos = json.load(f)
            if self.indice_actual is not None and 0 <= self.indice_actual < len(self.datos):
                self.actual = self.datos[self.indice_actual]
            else:
                self.kanji_aleatorio()
            self.mostrar_palabra_actual()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo recargar:\n{e}")

    # ---------------------- Mostrar palabra ----------------------
    def mostrar_palabra_actual(self):
        if not self.actual:
            self.label_kanji.config(text="", fg="white")
            for lbl in [self.label_espanol, self.label_ingles,
                        self.label_pinyin, self.label_onyomi, self.label_on_romaji,
                        self.label_kunyomi, self.label_kun_romaji]:
                lbl.config(text="", fg="white")
            if self.table_examples:
                self.table_examples.destroy()
                self.table_examples = None
            self.label_indice.config(text="")
            return

        kanji_valor = self.actual.get("kanji", "")
        if kanji_valor and str(kanji_valor).strip():
            self.label_kanji.config(text=kanji_valor, fg="white")
        else:
            self.label_kanji.config(text="### Falta kanji ###", fg="red")

        campos = [
            ("spanish", self.label_espanol),
            ("english", self.label_ingles),
            ("pinyin", self.label_pinyin),
            ("onyomi", self.label_onyomi),
            ("on_romaji", self.label_on_romaji),
            ("kunyomi", self.label_kunyomi),
            ("kun_romaji", self.label_kun_romaji),
        ]
        for key, label in campos:
            valor = self.actual.get(key, "")
            nombre = self.display_names.get(key, key)
            if valor and str(valor).strip():
                label.config(text=f"{nombre}: {valor}", fg="#116eef")
            else:
                label.config(text=f"### Falta {nombre} ###", fg="red")

        self._mostrar_tabla_examples()

        if self.indice_actual is not None:
            self.label_indice.config(text=f"Índice actual: {self.indice_actual + 1} / {len(self.datos)}")
        else:
            self.label_indice.config(text="")

    def _mostrar_tabla_examples(self):
        if self.table_examples:
            self.table_examples.destroy()
        self.table_examples = tk.Frame(self.frame_example, bg="#000000")
        self.table_examples.pack()

        headers = ["Example", "Example kana", "(Romaji)", "(ESpañol)", "(ENglish)"]
        for j, h in enumerate(headers):
            tk.Label(self.table_examples, text=h, font=("Arial", 14, "bold"),
                     fg="cyan", bg="#000000", borderwidth=1, relief="solid", width=25).grid(row=0, column=j, sticky="nsew")

        valores = [
            self.actual.get("example", ""),
            self.actual.get("example_kana", ""),
            self.actual.get("example_ro", ""),
            self.actual.get("example_es", ""),
            self.actual.get("example_en", "")
        ]

        for j, val in enumerate(valores):
            texto = val if val and str(val).strip() else f"### Falta {headers[j]} ###"
            fg_color = "white" if val and str(val).strip() else "red"
            tk.Label(self.table_examples, text=texto, font=("Arial", 12), wraplength=300,
                     fg=fg_color, bg="#000000", borderwidth=1, relief="solid", width=25, justify="center").grid(row=1, column=j, sticky="nsew")

    # ---------------------- Navegación ----------------------
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
        self.indice_actual = random.randrange(len(self.datos))
        self.actual = self.datos[self.indice_actual]
        self.mostrar_palabra_actual()

    def kanji_siguiente(self):
        if not self.datos:
            return
        if self.indice_actual is None:
            self.indice_actual = 0
        self.indice_actual = (self.indice_actual + 1) % len(self.datos)
        self.actual = self.datos[self.indice_actual]
        self.mostrar_palabra_actual()

    # ---------------------- Utilidades ----------------------
    def copiar_kanji(self):
        if self.actual and "kanji" in self.actual and self.actual.get("kanji"):
            try:
                self.master.clipboard_clear()
                self.master.clipboard_append(str(self.actual["kanji"]))
            except:
                pass

    def abrir_diccionario(self):
        if self.actual and "kanji" in self.actual and self.actual.get("kanji"):
            kanji = self.actual["kanji"]
            webbrowser.open(f"https://jisho.org/search/{kanji}")

    # ---------------------- Edición ----------------------
    def mostrar_datos(self):
        if not self.actual:
            return
        if self.ventana_edicion and self.ventana_edicion.winfo_exists():
            self.ventana_edicion.lift()
            return

        campos = ["kanji", "pinyin", "onyomi", "on_romaji", "kunyomi", "kun_romaji",
                  "spanish", "english",
                  "example", "example_kana", "example_ro", "example_es", "example_en"]

        self.ventana_edicion = tk.Toplevel(self.master)
        self.ventana_edicion.title("Editar")
        self.ventana_edicion.configure(bg="black")
        self.ventana_edicion.geometry("900x700")

        canvas = tk.Canvas(self.ventana_edicion, bg="black")
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(self.ventana_edicion, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        frame_campos = tk.Frame(canvas, bg="black")
        canvas.create_window((0, 0), window=frame_campos, anchor="nw")

        entries = {}

        frame_botones_arriba = tk.Frame(frame_campos, bg="black")
        frame_botones_arriba.pack(fill="x", pady=10)

        btn_guardar = tk.Button(frame_botones_arriba, text="Guardar cambios", bg="#00cc00", fg="white", font=("Arial", 14, "bold"))
        btn_guardar.pack(side="left", padx=10)

        btn_eliminar = tk.Button(frame_botones_arriba, text="Eliminar esta palabra", bg="red", fg="white", font=("Arial", 14, "bold"))
        btn_eliminar.pack(side="left", padx=10)

        for campo in campos:
            tk.Label(frame_campos, text=self.display_names.get(campo, campo), fg="white", bg="black",
                     font=("Arial", 14, "bold")).pack(pady=(10, 0), anchor="w")
            if campo.startswith("example"):
                text_widget = tk.Text(frame_campos, width=100, height=5, font=("Arial", 14))
                text_widget.insert("1.0", str(self.actual.get(campo, "")))
                text_widget.pack()
                entries[campo] = text_widget
            else:
                entry = tk.Entry(frame_campos, width=100, font=("Arial", 14))
                entry.insert(0, str(self.actual.get(campo, "")))
                entry.pack()
                entries[campo] = entry

        def guardar_cambios():
            for k, widget in entries.items():
                if k.startswith("example"):
                    valor = widget.get("1.0", "end-1c")
                    self.actual[k] = valor
                else:
                    self.actual[k] = widget.get()
            if not self.ruta_json:
                messagebox.showwarning("Guardar", "No hay archivo JSON cargado para guardar.")
                return
            try:
                with open(self.ruta_json, "w", encoding="utf-8") as f:
                    json.dump(self.datos, f, ensure_ascii=False, indent=4)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{e}")
                return
            self.mostrar_palabra_actual()
            try:
                self.ventana_edicion.destroy()
            except:
                pass
            self.ventana_edicion = None
            messagebox.showinfo("Guardado", "Cambios guardados correctamente.")

        def eliminar_palabra():
            if messagebox.askyesno("Eliminar", "¿Seguro que quieres eliminar esta palabra?"):
                try:
                    self.datos.pop(self.indice_actual)
                    if self.ruta_json:
                        with open(self.ruta_json, "w", encoding="utf-8") as f:
                            json.dump(self.datos, f, ensure_ascii=False, indent=4)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")
                    return
                try:
                    self.ventana_edicion.destroy()
                except:
                    pass
                self.ventana_edicion = None
                if self.datos:
                    self.indice_actual = min(self.indice_actual, len(self.datos) - 1) if self.indice_actual is not None else 0
                    self.actual = self.datos[self.indice_actual]
                else:
                    self.actual = None
                    self.indice_actual = None
                self.mostrar_palabra_actual()
                messagebox.showinfo("Eliminado", "Palabra eliminada correctamente.")

        btn_guardar.config(command=guardar_cambios)
        btn_eliminar.config(command=eliminar_palabra)

        def actualizar_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        frame_campos.bind("<Configure>", actualizar_scroll)

    # ---------------------- JSON SEGURO ----------------------
    def editar_json_actual(self):
        if not self.actual:
            return
        if not self.ruta_json:
            messagebox.showwarning("Editar JSON", "No hay archivo JSON cargado para editar.")
            return
        if hasattr(self, 'ventana_json') and self.ventana_json.winfo_exists():
            self.ventana_json.lift()
            return

        self.ventana_json = tk.Toplevel(self.master)
        self.ventana_json.title("Editar JSON")
        self.ventana_json.geometry("800x600")
        self.ventana_json.configure(bg="black")

        frame_top = tk.Frame(self.ventana_json, bg="black")
        frame_top.pack(fill="x", padx=10, pady=5)

        lbl_error = tk.Label(frame_top, text="", fg="red", bg="black", font=("Arial", 12, "bold"))
        lbl_error.pack(side="left", padx=5)

        btn_guardar = tk.Button(frame_top, text="Guardar cambios", bg="#00cc00", fg="white", font=("Arial", 14, "bold"))
        btn_guardar.pack(side="right", padx=5)

        text_json = tk.Text(self.ventana_json, font=("Consolas", 12), bg="black", fg="white")
        text_json.pack(expand=True, fill="both", padx=10, pady=10)
        text_json.insert("1.0", json.dumps(self.actual, ensure_ascii=False, indent=4))

        btn_guardar.config(state=tk.DISABLED)

        def validar_json(event=None):
            contenido = text_json.get("1.0", "end-1c")
            try:
                json.loads(contenido)
                lbl_error.config(text="")
                btn_guardar.config(state=tk.NORMAL)
            except json.JSONDecodeError as e:
                lbl_error.config(text=f"Error JSON: {e}")
                btn_guardar.config(state=tk.DISABLED)

        def guardar_json():
            contenido = text_json.get("1.0", "end-1c")
            try:
                nuevo_obj = json.loads(contenido)
                self.datos[self.indice_actual] = nuevo_obj
                with open(self.ruta_json, "w", encoding="utf-8") as f:
                    json.dump(self.datos, f, ensure_ascii=False, indent=4)
                self.actual = nuevo_obj
                self.mostrar_palabra_actual()
                self.ventana_json.destroy()
                messagebox.showinfo("Guardado", "JSON actualizado correctamente.")
            except json.JSONDecodeError:
                messagebox.showerror("Error JSON", "No se puede guardar, JSON inválido.")

        text_json.bind("<<Modified>>", lambda e: (validar_json(), text_json.edit_modified(0)))
        btn_guardar.config(command=guardar_json)
        validar_json()

    # ---------------------- Ir a campo vacío ----------------------
    def ir_campo_vacio(self):
        if not self.datos:
            return
        for i, palabra in enumerate(self.datos):
            for campo in ["kanji", "pinyin", "onyomi", "on_romaji",
                          "kunyomi", "kun_romaji", "spanish", "english",
                          "example", "example_kana", "example_ro", "example_es", "example_en"]:
                if not str(palabra.get(campo, "")).strip():
                    self.indice_actual = i
                    self.actual = palabra
                    self.mostrar_palabra_actual()
                    return
        messagebox.showinfo("Campos vacíos", "No se encontraron palabras con campos vacíos.")

    # ---------------------- Ir a example largo ----------------------
    def ir_example_largo(self):
        if not self.datos:
            return
        for i, palabra in enumerate(self.datos):
            if any(len(str(palabra.get(campo, ""))) > 200
                   for campo in ["example", "example_kana", "example_ro", "example_es", "example_en"]):
                self.indice_actual = i
                self.actual = palabra
                self.mostrar_palabra_actual()
                return
        messagebox.showinfo("Example largo", "No se encontraron ejemplos largos.")

    # ---------------------- Ir a corchetes ----------------------
    def detectar_corchetes1(self):
        if not self.datos:
            return
        for i, item in enumerate(self.datos):
            for valor in item.values():
                if isinstance(valor, str) and ("," in valor or ";" in valor):
                    self.actual = item
                    self.indice_actual = i
                    self.mostrar_palabra_actual()
                    return
        messagebox.showinfo("Sin resultados", "No se encontró ningún campo con , o ;.")

    def detectar_corchetes(self):
        if not self.datos:
            return
        for i, item in enumerate(self.datos):
            for valor in item.values():
                if isinstance(valor, str) and ("[" in valor or "]" in valor):
                    self.actual = item
                    self.indice_actual = i
                    self.mostrar_palabra_actual()
                    return
        messagebox.showinfo("Sin resultados", "No se encontró ningún campo con corchetes [ o ].")

    # ---------------------- Búsqueda ----------------------
    def abrir_busqueda(self):
        if not self.datos:
            return
        if self.ventana_busqueda and self.ventana_busqueda.winfo_exists():
            self.ventana_busqueda.lift()
            return

        self.ventana_busqueda = tk.Toplevel(self.master)
        self.ventana_busqueda.title("Buscar palabra")
        self.ventana_busqueda.configure(bg="black")
        self.ventana_busqueda.geometry("500x200")

        tk.Label(self.ventana_busqueda, text="Texto a buscar:", fg="white", bg="black", font=("Arial", 14)).pack(pady=10)
        entry_busqueda = tk.Entry(self.ventana_busqueda, width=50, font=("Arial", 14))
        entry_busqueda.pack(pady=5)

        frame_botones = tk.Frame(self.ventana_busqueda, bg="black")
        frame_botones.pack(pady=10)

        def ejecutar_busqueda():
            texto = entry_busqueda.get().strip().lower()
            if not texto:
                return
            self.resultados_busqueda = []
            for i, palabra in enumerate(self.datos):
                for valor in palabra.values():
                    if isinstance(valor, str) and texto in valor.lower():
                        self.resultados_busqueda.append(i)
                        break
            if not self.resultados_busqueda:
                messagebox.showinfo("Sin resultados", "No se encontraron coincidencias.")
                return
            self.indice_resultado = 0
            self.ir_a_resultado()

        def siguiente_resultado():
            if not self.resultados_busqueda:
                return
            self.indice_resultado = (self.indice_resultado + 1) % len(self.resultados_busqueda)
            self.ir_a_resultado()

        def anterior_resultado():
            if not self.resultados_busqueda:
                return
            self.indice_resultado = (self.indice_resultado - 1) % len(self.resultados_busqueda)
            self.ir_a_resultado()

        btn_buscar = tk.Button(frame_botones, text="Buscar", command=ejecutar_busqueda)
        btn_buscar.pack(side="left", padx=5)
        btn_anterior = tk.Button(frame_botones, text="Anterior", command=anterior_resultado)
        btn_anterior.pack(side="left", padx=5)
        btn_siguiente = tk.Button(frame_botones, text="Siguiente", command=siguiente_resultado)
        btn_siguiente.pack(side="left", padx=5)

    def ir_a_resultado(self):
        if not self.resultados_busqueda:
            return
        idx = self.resultados_busqueda[self.indice_resultado]
        self.indice_actual = idx
        self.actual = self.datos[idx]
        self.mostrar_palabra_actual()
        if self.ventana_busqueda and self.ventana_busqueda.winfo_exists():
            self.ventana_busqueda.title(f"Buscar palabra ({self.indice_resultado + 1}/{len(self.resultados_busqueda)})")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)

    # Bind Ctrl+M para ir al primer campo vacío
    root.bind("<Control-0>", lambda event: app.ir_campo_vacio())
    root.bind("<Control-o>", lambda event: app.ir_campo_vacio())
    root.bind("<Control-q>", lambda event: app.ir_campo_vacio())

    # Bind Ctrl+w para editar los datos del bloque de json actual

    root.bind("<Control-j>", lambda event: app.editar_json_actual())
    root.bind("<Control-w>", lambda event: app.editar_json_actual())



    # Bind Ctrl+E para editar los datos de la palabra actual
    root.bind("<Control-e>", lambda event: app.mostrar_datos())
    root.bind("<Control-t>", lambda event: app.mostrar_datos())

    # Ctrl+F para buscar
    root.bind("<Control-f>", lambda event: app.abrir_busqueda())


    # Flechas para navegar
    root.bind("<Right>", lambda event: app.kanji_siguiente())
    root.bind("<Left>", lambda event: app.kanji_anterior())




    # Flechas arriba/abajo para kanji aleatorio
    root.bind("<Up>", lambda event: app.kanji_aleatorio())
    root.bind("<Down>", lambda event: app.kanji_aleatorio())



    
    root.mainloop()
