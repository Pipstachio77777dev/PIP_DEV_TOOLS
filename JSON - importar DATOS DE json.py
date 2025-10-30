import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import json

class ImportarAlMazoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Importar al Mazo")

        self.json1 = []
        self.json2 = []
        self.json1_path = None
        self.campo_clave = "kanji"

        # Botones
        tk.Button(root, text="Seleccionar Primer JSON", command=self.seleccionar_primer_json).pack(pady=4)
        tk.Button(root, text="Seleccionar Segundo JSON", command=self.seleccionar_segundo_json).pack(pady=4)
        tk.Button(root, text="Comparar por Campo", command=self.comparar_por_campo).pack(pady=4)
        tk.Button(root, text="Actualizar Coincidencias", command=self.actualizar_coincidencias).pack(pady=4)
        tk.Button(root, text="Fusionar Coincidencias", command=self.fusionar_coincidencias).pack(pady=4)
        tk.Button(root, text="Agregar Nuevos del Segundo JSON", command=self.agregar_nuevos).pack(pady=4)
        tk.Button(root, text="Guardar Cambios", command=self.guardar_cambios).pack(pady=8)

        self.estado = tk.Label(root, text="Esperando selección de archivos...", fg="blue")
        self.estado.pack(pady=10)

    def seleccionar_primer_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                self.json1 = json.load(f)
            self.json1_path = path
            self.actualizar_estado()

    def seleccionar_segundo_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                self.json2 = json.load(f)
            self.actualizar_estado()

    def actualizar_estado(self):
        texto = f"Primer JSON: {len(self.json1)} elementos | Segundo JSON: {len(self.json2)} elementos"
        self.estado.config(text=texto)

    def pedir_campo_clave(self):
        campo = simpledialog.askstring("Campo clave", "¿Qué campo usar para comparar? (ej. 'kanji' o 'word')", initialvalue=self.campo_clave)
        if campo:
            self.campo_clave = campo
        return campo

    def comparar_por_campo(self):
        if not self.json1 or not self.json2:
            messagebox.showerror("Error", "Selecciona ambos archivos JSON.")
            return
        campo = self.pedir_campo_clave()
        if not campo:
            return

        claves1 = {item[campo] for item in self.json1 if campo in item}
        claves2 = {item[campo] for item in self.json2 if campo in item}
        coincidencias = claves1 & claves2
        messagebox.showinfo("Comparación", f"Se encontraron {len(coincidencias)} coincidencias por el campo '{campo}'.")

    def actualizar_coincidencias(self):
        if not self.json1 or not self.json2:
            messagebox.showerror("Error", "Selecciona ambos archivos JSON.")
            return
        campo = self.pedir_campo_clave()
        if not campo:
            return

        dict1 = {item[campo]: item for item in self.json1 if campo in item}
        dict2 = {item[campo]: item for item in self.json2 if campo in item}
        coincidencias = set(dict1.keys()) & set(dict2.keys())

        for clave in coincidencias:
            dict1[clave] = dict2[clave]  # reemplaza completamente

        self.json1 = list(dict1.values())
        self.actualizar_estado()
        messagebox.showinfo("Actualización completa", f"Se actualizaron {len(coincidencias)} entradas.")

    def fusionar_coincidencias(self):
        if not self.json1 or not self.json2:
            messagebox.showerror("Error", "Selecciona ambos archivos JSON.")
            return
        campo = self.pedir_campo_clave()
        if not campo:
            return

        dict1 = {item[campo]: item for item in self.json1 if campo in item}
        dict2 = {item[campo]: item for item in self.json2 if campo in item}
        coincidencias = set(dict1.keys()) & set(dict2.keys())

        for clave in coincidencias:
            dict1[clave].update(dict2[clave])  # fusiona campo por campo

        self.json1 = list(dict1.values())
        self.actualizar_estado()
        messagebox.showinfo("Fusión completa", f"Se fusionaron {len(coincidencias)} entradas.")

    def agregar_nuevos(self):
        if not self.json1 or not self.json2:
            messagebox.showerror("Error", "Selecciona ambos archivos JSON.")
            return
        campo = self.campo_clave
        claves1 = {item[campo] for item in self.json1 if campo in item}
        nuevos = [item for item in self.json2 if campo in item and item[campo] not in claves1]

        self.json1.extend(nuevos)
        self.actualizar_estado()
        messagebox.showinfo("Agregados", f"Se agregaron {len(nuevos)} nuevos elementos.")

    def guardar_cambios(self):
        if not self.json1:
            messagebox.showerror("Error", "No hay datos para guardar.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.json1, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Guardado", f"Archivo guardado en: {path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImportarAlMazoApp(root)
    root.mainloop()
