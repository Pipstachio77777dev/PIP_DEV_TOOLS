import tkinter as tk
from tkinter import filedialog, messagebox
import ast
import re

class FunctionRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Function Renamer")
        
        self.filename = None
        self.code = ""
        self.tree = None
        self.functions = []

        # Widgets
        self.open_button = tk.Button(root, text="Abrir archivo .py", command=self.open_file)
        self.open_button.pack(pady=5)

        self.func_listbox = tk.Listbox(root)
        self.func_listbox.pack(pady=5, fill=tk.BOTH, expand=True)

        self.rename_frame = tk.Frame(root)
        self.rename_frame.pack(pady=5)

        self.new_name_entry = tk.Entry(self.rename_frame)
        self.new_name_entry.pack(side=tk.LEFT, padx=5)
        self.rename_button = tk.Button(self.rename_frame, text="Renombrar función", command=self.rename_function)
        self.rename_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(root, text="Guardar cambios", command=self.save_file)
        self.save_button.pack(pady=5)

    def open_file(self):
        self.filename = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if not self.filename:
            return
        
        with open(self.filename, "r", encoding="utf-8") as f:
            self.code = f.read()

        # Analiza el AST
        self.tree = ast.parse(self.code)
        self.extract_functions()
    
    def extract_functions(self):
        # Encuentra todas las funciones usando AST
        self.functions = [node.name for node in ast.walk(self.tree) if isinstance(node, ast.FunctionDef)]
        
        # Ordena alfabéticamente
        self.functions.sort()
        
        # Actualiza la lista en la interfaz
        self.func_listbox.delete(0, tk.END)
        for func in self.functions:
            self.func_listbox.insert(tk.END, func)

    def rename_function(self):
        selected = self.func_listbox.curselection()
        new_name = self.new_name_entry.get().strip()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona una función de la lista")
            return
        if not new_name:
            messagebox.showwarning("Advertencia", "Ingresa un nuevo nombre para la función")
            return

        old_name = self.functions[selected[0]]

        # Reemplaza solo definiciones y llamadas usando regex seguro
        # \b asegura que solo se reemplacen nombres exactos
        pattern = rf'\b{old_name}\b'
        self.code = re.sub(pattern, new_name, self.code)
        
        self.functions[selected[0]] = new_name
        self.func_listbox.delete(selected[0])
        self.func_listbox.insert(selected[0], new_name)

        messagebox.showinfo("Éxito", f"Función '{old_name}' renombrada a '{new_name}'")
    
    def save_file(self):
        if not self.filename:
            return
        save_as = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
        if not save_as:
            return
        with open(save_as, "w", encoding="utf-8") as f:
            f.write(self.code)
        messagebox.showinfo("Éxito", "Archivo guardado correctamente")

if __name__ == "__main__":
    root = tk.Tk()
    app = FunctionRenamerApp(root)
    root.geometry("400x400")
    root.mainloop()
