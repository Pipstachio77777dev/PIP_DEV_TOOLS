import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os

def convertir_a_ico():
    # Abrir diálogo para seleccionar imagen PNG o JPG
    archivo = filedialog.askopenfilename(
        title="Seleccionar imagen PNG o JPG",
        filetypes=[("Imágenes", "*.png *.jpg *.jpeg")]
    )
    if not archivo:
        return  # Si no seleccionó archivo, salir

    try:
        # Abrir la imagen con PIL
        imagen = Image.open(archivo)
        
        # Ruta para guardar el icono (misma carpeta, mismo nombre, extensión .ico)
        carpeta = os.path.dirname(archivo)
        nombre_sin_ext = os.path.splitext(os.path.basename(archivo))[0]
        ruta_ico = os.path.join(carpeta, nombre_sin_ext + ".ico")
        
        # Convertir y guardar como icono (tamaños típicos: 16x16, 32x32, 48x48)
        imagen.save(ruta_ico, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128)])
        
        messagebox.showinfo("Éxito", f"Icono creado en:\n{ruta_ico}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo convertir la imagen:\n{e}")

# Crear ventana principal
root = tk.Tk()
root.title("Convertidor de imagen a icono")
root.geometry("300x150")
root.resizable(False, False)

# Botón para seleccionar imagen y convertir
btn_convertir = tk.Button(root, text="Seleccionar imagen y convertir a .ico", command=convertir_a_ico)
btn_convertir.pack(expand=True)

root.mainloop()
