import tkinter as tk
from tkinter import filedialog, messagebox
import json
import random

class FrasesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Frases App")
        self.root.geometry("900x600")

        self.frases_data = []
        self.index = 0
        self.selected_words = []
        self.shuffled_words = []
        self.resultado = None
        self.mostrar_lectura = False
        self.file_path = None

        # Botón para cargar JSON
        self.load_button = tk.Button(root, text="Cargar JSON", command=self.load_json)
        self.load_button.pack(pady=10)

        # Contenedor de botones de navegación
        self.nav_frame = tk.Frame(root)
        self.nav_frame.pack(pady=5)

        self.prev_button = tk.Button(self.nav_frame, text="Anterior", command=self.show_previous)
        self.prev_button.grid(row=0, column=0, padx=5)

        self.next_button = tk.Button(self.nav_frame, text="Siguiente", command=self.show_next)
        self.next_button.grid(row=0, column=1, padx=5)

        self.next_random_button = tk.Button(self.nav_frame, text="Siguiente (aleatoria)", command=self.show_next_random)
        self.next_random_button.grid(row=0, column=2, padx=5)

        self.show_reading_button = tk.Button(self.nav_frame, text="Mostrar lectura", command=self.show_reading, state="disabled")
        self.show_reading_button.grid(row=0, column=3, padx=5)

        self.edit_button = tk.Button(self.nav_frame, text="Editar", command=self.edit_frase, state="disabled")
        self.edit_button.grid(row=0, column=4, padx=5)

        self.add_button = tk.Button(self.nav_frame, text="Agregar", command=self.add_frase, state="disabled")
        self.add_button.grid(row=0, column=5, padx=5)

        self.delete_button = tk.Button(self.nav_frame, text="Eliminar", command=self.delete_frase, state="disabled")
        self.delete_button.grid(row=0, column=6, padx=5)

        self.show_all_button = tk.Button(self.nav_frame, text="Mostrar todas", command=self.show_all, state="disabled")
        self.show_all_button.grid(row=0, column=7, padx=5)

        self.save_button = tk.Button(self.nav_frame, text="Guardar JSON", command=self.save_json, state="disabled")
        self.save_button.grid(row=0, column=8, padx=5)

        # Contador
        self.counter_label = tk.Label(root, text="")
        self.counter_label.pack(pady=5)

        # Frase correcta
        self.kanji_label = tk.Label(root, text="", font=("Arial", 32), fg="#d32f2f")
        self.kanji_label.pack(pady=5)

        # Palabras seleccionadas
        self.selected_frame = tk.Frame(root)
        self.selected_frame.pack(pady=5)

        # Palabras desordenadas
        self.shuffled_frame = tk.Frame(root)
        self.shuffled_frame.pack(pady=5)

        # Botón comprobar
        self.check_button = tk.Button(root, text="Comprobar", command=self.comprobar)
        self.check_button.pack(pady=5)

        # Resultado
        self.result_label = tk.Label(root, text="", font=("Arial", 18), fg="#d32f2f")
        self.result_label.pack(pady=5)

        # Traducciones
        self.traductions_frame = tk.Frame(root)
        self.traductions_frame.pack(pady=10)

    # ---------------- FUNCIONES PRINCIPALES ----------------

    def load_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.frases_data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")
            return
        self.file_path = file_path
        self.index = 0
        self.enable_buttons()
        self.load_frase()

    def save_json(self):
        if not self.frases_data:
            messagebox.showwarning("Guardar", "No hay datos para guardar.")
            return
        if not self.file_path:
            path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if not path:
                return
            self.file_path = path
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.frases_data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Guardado", f"Archivo guardado en:\n{self.file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

    def enable_buttons(self):
        self.edit_button.config(state="normal")
        self.add_button.config(state="normal")
        self.delete_button.config(state="normal")
        self.show_all_button.config(state="normal")
        self.save_button.config(state="normal")

    def shuffle_array(self, array):
        new_arr = array[:]
        random.shuffle(new_arr)
        return new_arr

    def load_frase(self):
        if not self.frases_data:
            self.counter_label.config(text="0/0")
            self.kanji_label.config(text="")
            return

        self.selected_words = []
        self.resultado = None
        self.mostrar_lectura = False
        self.show_reading_button.config(state="disabled")
        self.result_label.config(text="")
        self.kanji_label.config(text="")

        self.frase = self.frases_data[self.index]
        palabras = self.frase.get("kanji", "").strip().split()
        self.shuffled_words = self.shuffle_array(palabras)

        self.update_ui()

    def update_ui(self):
        total = len(self.frases_data)
        self.counter_label.config(text=f"{self.index + 1} / {total}")

        for widget in self.selected_frame.winfo_children():
            widget.destroy()
        for word in self.selected_words:
            btn = tk.Button(self.selected_frame, text=word, command=lambda w=word: self.remove_word(w), bg="#E8F5E9")
            btn.pack(side="left", padx=2)

        for widget in self.shuffled_frame.winfo_children():
            widget.destroy()
        for word in self.shuffled_words:
            btn = tk.Button(self.shuffled_frame, text=word, command=lambda w=word: self.select_word(w))
            btn.pack(side="left", padx=2)

        if self.resultado == "✅ Correcto":
            self.kanji_label.config(text=self.frase.get("kanji", ""))

    # ---------------- INTERACCIÓN PALABRAS ----------------

    def select_word(self, word):
        self.selected_words.append(word)
        self.shuffled_words.remove(word)
        self.update_ui()

    def remove_word(self, word):
        self.shuffled_words.append(word)
        self.selected_words.remove(word)
        self.update_ui()

    def comprobar(self):
        original = self.frase.get("kanji", "").replace(" ", "")
        respuesta = "".join(self.selected_words)
        self.resultado = "✅ Correcto" if respuesta == original else "❌ Incorrecto"
        self.result_label.config(text=self.resultado)
        if self.resultado == "✅ Correcto":
            self.show_reading_button.config(state="normal")
        self.update_ui()

    # ---------------- NAVEGACIÓN ----------------

    def show_previous(self):
        if not self.frases_data:
            return
        self.index = (self.index - 1) % len(self.frases_data)
        self.load_frase()

    def show_next(self):
        if not self.frases_data:
            return
        self.index = (self.index + 1) % len(self.frases_data)
        self.load_frase()

    def show_next_random(self):
        if not self.frases_data:
            return
        new_index = random.randint(0, len(self.frases_data) - 1)
        while new_index == self.index and len(self.frases_data) > 1:
            new_index = random.randint(0, len(self.frases_data) - 1)
        self.index = new_index
        self.load_frase()

    # ---------------- LECTURA Y TRADUCCIÓN ----------------

    def show_reading(self):
        for widget in self.traductions_frame.winfo_children():
            widget.destroy()

        labels = [
            ("Furigana", self.frase.get("furigana", "")),
            ("Romaji", self.frase.get("romaji", "")),
            ("Inglés", self.frase.get("ingles", "")),
            ("Español", self.frase.get("español", "")),
            ("Portugués", self.frase.get("portugues") or self.frase.get("portuges", ""))
        ]

        for label_text, value in labels:
            lbl = tk.Label(self.traductions_frame, text=f"{label_text}: {value}", font=("Arial", 20))
            lbl.pack()

    # ---------------- CRUD FRASES ----------------

    def edit_frase(self):
        if not self.frases_data:
            return

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar frase")
        edit_window.geometry("400x400")

        entries = {}
        fields = ["kanji", "furigana", "romaji", "ingles", "español", "portugues"]

        for i, field in enumerate(fields):
            tk.Label(edit_window, text=field.capitalize()).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            entry = tk.Entry(edit_window, width=40)
            entry.insert(0, self.frase.get(field, ""))
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry

        def save_edits():
            for field, entry in entries.items():
                self.frase[field] = entry.get()
            messagebox.showinfo("Guardado", "Frase editada correctamente.")
            edit_window.destroy()
            self.load_frase()

        tk.Button(edit_window, text="Guardar", command=save_edits).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def add_frase(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Agregar frase")
        add_window.geometry("400x400")

        entries = {}
        fields = ["kanji", "furigana", "romaji", "ingles", "español", "portugues"]

        for i, field in enumerate(fields):
            tk.Label(add_window, text=field.capitalize()).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            entry = tk.Entry(add_window, width=40)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry

        def save_new():
            new_frase = {field: entry.get() for field, entry in entries.items()}
            self.frases_data.append(new_frase)
            messagebox.showinfo("Guardado", "Frase agregada correctamente.")
            add_window.destroy()
            self.index = len(self.frases_data) - 1
            self.load_frase()

        tk.Button(add_window, text="Guardar", command=save_new).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def delete_frase(self):
        if not self.frases_data:
            return
        confirm = messagebox.askyesno("Eliminar", "¿Seguro que quieres eliminar esta frase?")
        if confirm:
            del self.frases_data[self.index]
            if self.index >= len(self.frases_data):
                self.index = max(0, len(self.frases_data) - 1)
            if self.frases_data:
                self.load_frase()
            else:
                self.kanji_label.config(text="")
                self.counter_label.config(text="0/0")
                self.result_label.config(text="")
                for frame in [self.selected_frame, self.shuffled_frame, self.traductions_frame]:
                    for widget in frame.winfo_children():
                        widget.destroy()
                messagebox.showinfo("Vacío", "Ya no quedan frases.")

    def show_all(self):
        if not self.frases_data:
            return

        all_window = tk.Toplevel(self.root)
        all_window.title("Todas las frases")
        all_window.geometry("700x400")

        canvas = tk.Canvas(all_window)
        scrollbar = tk.Scrollbar(all_window, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for i, frase in enumerate(self.frases_data, start=1):
            text = f"{i}. {frase.get('kanji', '')} | {frase.get('español', '')} | {frase.get('ingles', '')}"
            lbl = tk.Label(scroll_frame, text=text, font=("Arial", 14), anchor="w", justify="left")
            lbl.pack(fill="x", padx=5, pady=2)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

if __name__ == "__main__":
    root = tk.Tk()
    app = FrasesApp(root)
    root.mainloop()