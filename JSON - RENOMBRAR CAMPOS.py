import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

class JsonEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor JSON con Tkinter")

        self.data = []
        self.filepath = None
        self.campos = set()

        # Botones arriba
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Abrir JSON", command=self.abrir_json).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Guardar JSON", command=self.guardar_json).pack(side=tk.LEFT, padx=5)


        # Lista elementos
        self.listbox = tk.Listbox(root, selectmode=tk.EXTENDED, width=80, height=20)
        self.listbox.pack(padx=10, pady=10)

        # Lista campos y botón renombrar campo seleccionado
        campos_frame = tk.Frame(root)
        campos_frame.pack(fill=tk.X, padx=10)

        tk.Label(campos_frame, text="Campos detectados:").pack(anchor='w')

        self.campos_listbox = tk.Listbox(campos_frame, height=6)
        self.campos_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)

        btn_renombrar_campo = tk.Button(campos_frame, text="Renombrar campo seleccionado", command=self.renombrar_campo_global)
        btn_renombrar_campo.pack(side=tk.LEFT, padx=5)

    def abrir_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.data = json.load(f)

            self.filepath = path
            self.actualizar_campos()
            self.refrescar_lista()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")

    def guardar_json(self):
        if not self.filepath:
            messagebox.showwarning("Atención", "No hay archivo abierto")
            return
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Éxito", "Archivo guardado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

    def refrescar_lista(self):
        self.listbox.delete(0, tk.END)
        for i, elem in enumerate(self.data):
            resumen = ", ".join(f"{k}: {v}" for k, v in elem.items())
            self.listbox.insert(tk.END, f"[{i}] {resumen}")

    def actualizar_campos(self):
        campos_unicos = set()
        for elem in self.data:
            if isinstance(elem, dict):
                campos_unicos.update(elem.keys())
        self.campos = campos_unicos

        self.campos_listbox.delete(0, tk.END)
        for campo in sorted(self.campos):
            self.campos_listbox.insert(tk.END, campo)

    def eliminar_seleccionados(self):
        selected = list(self.listbox.curselection())
        if not selected:
            messagebox.showwarning("Atención", "No hay elementos seleccionados")
            return
        for index in reversed(selected):
            self.data.pop(index)
        self.actualizar_campos()
        self.refrescar_lista()

    def renombrar_campo_lote(self):
        selected = list(self.listbox.curselection())
        if not selected:
            messagebox.showwarning("Atención", "Selecciona al menos un elemento")
            return

        campo_viejo = simpledialog.askstring("Renombrar campo", "Nombre actual del campo a renombrar:")
        if not campo_viejo:
            return

        campo_nuevo = simpledialog.askstring("Renombrar campo", "Nuevo nombre para el campo:")
        if not campo_nuevo:
            return

        for idx in selected:
            if campo_nuevo in self.data[idx]:
                messagebox.showerror("Error", f"El campo '{campo_nuevo}' ya existe en el elemento índice {idx}")
                return

        cambios = 0
        for idx in selected:
            if campo_viejo in self.data[idx]:
                self.data[idx][campo_nuevo] = self.data[idx].pop(campo_viejo)
                cambios += 1

        messagebox.showinfo("Renombrar campo", f"Campo renombrado en {cambios} elementos")
        self.actualizar_campos()
        self.refrescar_lista()

    def renombrar_campo_global(self):
        selection = self.campos_listbox.curselection()
        if not selection:
            messagebox.showwarning("Atención", "Selecciona un campo para renombrar")
            return
        campo_viejo = self.campos_listbox.get(selection[0])

        campo_nuevo = simpledialog.askstring("Renombrar campo global", f"Nuevo nombre para el campo '{campo_viejo}':")
        if not campo_nuevo:
            return

        if campo_nuevo in self.campos:
            messagebox.showerror("Error", f"El campo '{campo_nuevo}' ya existe")
            return

        cambios = 0
        for elem in self.data:
            if campo_viejo in elem:
                elem[campo_nuevo] = elem.pop(campo_viejo)
                cambios += 1

        if cambios == 0:
            messagebox.showinfo("Renombrar campo global", f"No se encontró el campo '{campo_viejo}' en ningún elemento.")
        else:
            messagebox.showinfo("Renombrar campo global", f"Campo renombrado en {cambios} elementos")

        self.actualizar_campos()
        self.refrescar_lista()

    def agregar_elemento(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Agregar nuevo elemento")

        tk.Label(ventana, text="Nuevo elemento JSON:").pack(pady=5)
        text = tk.Text(ventana, width=60, height=10)
        text.pack(padx=10)

        def agregar():
            contenido = text.get("1.0", tk.END).strip()
            try:
                nuevo_elem = json.loads(contenido)
                if not isinstance(nuevo_elem, dict):
                    messagebox.showerror("Error", "El nuevo elemento debe ser un objeto JSON")
                    return
                self.data.append(nuevo_elem)
                self.actualizar_campos()
                self.refrescar_lista()
                ventana.destroy()
            except json.JSONDecodeError as e:
                messagebox.showerror("Error JSON", f"JSON inválido: {e}")

        tk.Button(ventana, text="Agregar", command=agregar).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = JsonEditorApp(root)
    root.mainloop()
