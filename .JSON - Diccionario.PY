import json
import tkinter as tk
from tkinter import filedialog, messagebox, Scrollbar, Listbox, END, Toplevel, Label, Entry, Button, font
import webbrowser

class VocabularioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vocabulario Japonés")
        self.root.geometry("600x600")
        self.root.configure(bg="black")

        self.vocabulario = []
        self.vocab_filtrado = []
        self.json_path = None
        self.palabra_seleccionada = None
        self.modo = "jp-es"
        self.busqueda = tk.StringVar()
        self.campos_totales = set()

        self.list_font = font.Font(family="Helvetica", size=16, weight="bold")

        # Frame superior botones
        self.frame_botones = tk.Frame(root, bg="black")
        self.frame_botones.pack(fill="x", padx=10, pady=5)

        self.btn_cargar_json = Button(
            self.frame_botones, text="Seleccionar JSON",
            command=self.cargar_json, bg="#00ffff", fg="black"
        )
        self.btn_cargar_json.pack(side="left", padx=5)

        self.btn_cambiar_modo = Button(
            self.frame_botones, text="Cambiar a Español / Japonés",
            command=self.cambiar_modo, bg="#ff00ff", fg="white"
        )
        self.btn_cambiar_modo.pack(side="left", padx=5)

        self.btn_agregar = Button(self.frame_botones, text="Agregar palabra", command=self.agregar_palabra, bg="#00ffff", fg="black")
        self.btn_agregar.pack(side="left", padx=5)

        # Botones que solo aparecen al seleccionar palabra
        self.btn_eliminar = Button(self.frame_botones, text="Eliminar palabra", command=self.eliminar_palabra, bg="#ff5555", fg="white")
        self.btn_editar = Button(self.frame_botones, text="Editar", command=self.editar_palabra, bg="#ffff00", fg="black")
        self.btn_jisho = Button(self.frame_botones, text="Jisho", command=self.buscar_jisho, bg="#ffaa00", fg="black")
        # Ocultos inicialmente
        self.btn_eliminar.pack_forget()
        self.btn_editar.pack_forget()
        self.btn_jisho.pack_forget()

        self.entry_busqueda = Entry(root, textvariable=self.busqueda, bg="black", fg="white", insertbackground="white")
        self.entry_busqueda.pack(fill="x", padx=10, pady=5)
        self.entry_busqueda.bind("<KeyRelease>", lambda event: self.actualizar_lista())

        self.scrollbar = Scrollbar(root)
        self.listbox = Listbox(root, bg="black", fg="white", selectbackground="#00ffff", yscrollcommand=self.scrollbar.set, font=self.list_font)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.mostrar_detalle)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.btn_volver = Button(root, text="Volver al Listado", command=self.volver_al_listado, bg="#00ffff", fg="black")
        self.btn_volver.pack(pady=10)
        self.btn_volver.pack_forget()

    # --- Métodos principales ---
    def cargar_json(self):
        self.json_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if self.json_path:
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    self.vocabulario = json.load(f)
                self.campos_totales = set()
                for palabra in self.vocabulario:
                    self.campos_totales.update(palabra.keys())
                for palabra in self.vocabulario:
                    for campo in self.campos_totales:
                        if campo not in palabra:
                            palabra[campo] = ""
                self.actualizar_lista()
                messagebox.showinfo("Éxito", "JSON cargado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el JSON:\n{e}")

    def cambiar_modo(self):
        self.modo = "es-jp" if self.modo == "jp-es" else "jp-es"
        texto = "Cambiar a Español / Japonés" if self.modo == "jp-es" else "Cambiar a Japonés / Español"
        self.btn_cambiar_modo.config(text=texto)
        self.actualizar_lista()

    def actualizar_lista(self):
        self.listbox.delete(0, END)
        query = self.busqueda.get().lower()
        self.vocab_filtrado = [
            p for p in self.vocabulario
            if any(str(p.get(k, "")).lower().find(query) != -1 for k in ["kanji", "romaji", "spanish", "english"])
        ]
        if self.modo == "jp-es":
            self.vocab_filtrado.sort(key=lambda x: str(x.get("kanji") or x.get("romaji") or "").lower())
        else:
            self.vocab_filtrado.sort(key=lambda x: str(x.get("spanish") or "").lower())
        for palabra in self.vocab_filtrado:
            display_text = f"{palabra.get('kanji') or palabra.get('romaji')} — {palabra.get('spanish')}" if self.modo == "jp-es" else f"{palabra.get('spanish')} — {palabra.get('kanji') or palabra.get('romaji')}"
            self.listbox.insert(END, display_text)

    # --- Mostrar detalle ---
    def mostrar_detalle(self, event):
        if not self.listbox.curselection() or self.palabra_seleccionada is not None:
            return
        index = self.listbox.curselection()[0]
        self.palabra_seleccionada = self.vocab_filtrado[index]

        self.listbox.delete(0, END)
        orden_campos = ["kanji","hanzi","hanzi_s","hanzi_t","word","pinyin","onyomi","kunyomi","furigana","romaji","ipa",
                        "spanish","english","portuguese",
                        "phrase_jp","phrase_cn_s","phrase_cn_t","phrase_es","phrase_en","phrase_es_t",
                        "latin","french","italian","german","japanese","chinese","korean","russian"]
        campos_extra = sorted(c for c in self.campos_totales if c not in orden_campos)
        for campo in orden_campos + campos_extra:
            if campo in self.palabra_seleccionada:
                self.listbox.insert(END, f"{campo.capitalize()}: {self.palabra_seleccionada.get(campo, '')}")

        self.btn_volver.pack(pady=10)
        self.btn_jisho.pack(side="left", padx=5)
        self.btn_editar.pack(side="left", padx=5)
        self.btn_eliminar.pack(side="left", padx=5)

    def volver_al_listado(self):
        self.palabra_seleccionada = None
        self.btn_volver.pack_forget()
        self.btn_jisho.pack_forget()
        self.btn_editar.pack_forget()
        self.btn_eliminar.pack_forget()
        self.actualizar_lista()

    # --- Agregar, eliminar, Jisho ---
    def agregar_palabra(self):
        nueva = {campo: "" for campo in self.campos_totales}
        self.vocabulario.append(nueva)
        self.actualizar_lista()
        self.palabra_seleccionada = nueva
        self.mostrar_detalle(None)

    def eliminar_palabra(self):
        if not self.palabra_seleccionada:
            return
        if messagebox.askyesno("Confirmar", "¿Deseas eliminar esta palabra?"):
            self.vocabulario.remove(self.palabra_seleccionada)
            self.palabra_seleccionada = None
            self.volver_al_listado()
            self.guardar_json()  # Guardar automáticamente al eliminar

    def buscar_jisho(self):
        if not self.palabra_seleccionada:
            return
        palabra = self.palabra_seleccionada.get("kanji") or self.palabra_seleccionada.get("romaji") or ""
        if palabra:
            webbrowser.open(f"https://jisho.org/search/{palabra}")

    # --- Editar palabra ---
    def editar_palabra(self):
        if not self.palabra_seleccionada:
            return
        self.ventana_edicion = Toplevel(self.root)
        self.ventana_edicion.title("Editar Palabra")
        self.ventana_edicion.geometry("600x700")
        self.ventana_edicion.configure(bg="black")

        canvas = tk.Canvas(self.ventana_edicion, bg="black")
        scrollbar = tk.Scrollbar(self.ventana_edicion, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        frame = tk.Frame(canvas, bg="black")
        canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self.entries = {}
        orden_campos = ["kanji","hanzi","hanzi_s","hanzi_t","word","pinyin","onyomi","kunyomi","furigana","romaji","ipa",
                        "spanish","english","portuguese",
                        "phrase_jp","phrase_cn_s","phrase_cn_t","phrase_es","phrase_en","phrase_es_t",
                        "latin","french","italian","german","japanese","chinese","korean","russian"]
        campos_extra = sorted(c for c in self.campos_totales if c not in orden_campos)

        first_entry = None
        for i, campo in enumerate(orden_campos + campos_extra):
            if campo in self.palabra_seleccionada:
                lbl = Label(frame, text=campo.capitalize(), bg="black", fg="#00ffff")
                lbl.grid(row=i, column=0, sticky="w", padx=10, pady=5)
                entry = Entry(frame, bg="black", fg="white", width=40, insertbackground="white")
                entry.grid(row=i, column=1, padx=10, pady=5, sticky="we")
                entry.insert(0, str(self.palabra_seleccionada.get(campo, "")))
                self.entries[campo] = entry
                if first_entry is None:
                    first_entry = entry
        if first_entry:
            first_entry.focus_set()
            first_entry.icursor(tk.END)

        self.btn_guardar_cambios = Button(frame, text="Guardar cambios", command=self.guardar_cambios_y_json, bg="#00ff00", fg="black")
        self.btn_guardar_cambios.grid(row=0, column=2, padx=5, pady=5, sticky="n")

    def guardar_cambios_y_json(self):
        # Guardar los cambios en la palabra seleccionada
        for campo, entry in self.entries.items():
            self.palabra_seleccionada[campo] = entry.get()
        # Cerrar ventana de edición
        self.ventana_edicion.destroy()
        # Actualizar lista y volver al listado
        self.palabra_seleccionada = None
        self.volver_al_listado()
        # Guardar todo el JSON
        self.guardar_json()

    # --- Guardar JSON ---
    def guardar_json(self):
        if not self.json_path:
            messagebox.showerror("Error", "No se ha seleccionado ningún JSON")
            return
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(self.vocabulario, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Éxito", "JSON guardado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el JSON:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VocabularioApp(root)
    root.mainloop()
