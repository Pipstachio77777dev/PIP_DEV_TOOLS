import tkinter as tk
from tkinter import messagebox
import random
import os
from PIL import Image
import colorsys



def generar_paletas_interface():
    hex_value = entrada.get()
    if len(hex_value) != 6:
        messagebox.showerror("Error", "Código hexadecimal inválido")
        return
    
    r = int(hex_value[0:2], 16)
    g = int(hex_value[2:4], 16)
    b = int(hex_value[4:6], 16)
    
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    
    ventana = tk.Toplevel(root)
    ventana.title("Paletas de colores para interfaz")
    
    # --- Original ---
    tk.Label(ventana, text="Original:").pack()
    tk.Label(ventana, bg=f"#{hex_value}", text=f"{hex_value}", fg="white").pack(fill="x")
    
    # --- Tema claro ---
    l_claro = min(l + 0.3, 1.0)
    r_cl, g_cl, b_cl = colorsys.hls_to_rgb(h, l_claro, s)
    r_cl, g_cl, b_cl = int(r_cl*255), int(g_cl*255), int(b_cl*255)
    hex_claro = rgb_a_hex(r_cl, g_cl, b_cl)
    tk.Label(ventana, text="Tema Claro:").pack()
    tk.Label(ventana, bg=f"#{hex_claro}", text=f"{hex_claro}", fg="black").pack(fill="x")
    
    # --- Tema oscuro ---
    l_oscuro = max(l - 0.3, 0.0)
    r_osc, g_osc, b_osc = colorsys.hls_to_rgb(h, l_oscuro, s)
    r_osc, g_osc, b_osc = int(r_osc*255), int(g_osc*255), int(b_osc*255)
    hex_oscuro = rgb_a_hex(r_osc, g_osc, b_osc)
    tk.Label(ventana, text="Tema Oscuro:").pack()
    tk.Label(ventana, bg=f"#{hex_oscuro}", text=f"{hex_oscuro}", fg="white").pack(fill="x")
    
    # --- Complementaria ---
    h_comp = (h + 0.5) % 1.0
    r_comp, g_comp, b_comp = colorsys.hls_to_rgb(h_comp, l, s)
    r_comp, g_comp, b_comp = int(r_comp*255), int(g_comp*255), int(b_comp*255)
    hex_comp = rgb_a_hex(r_comp, g_comp, b_comp)
    tk.Label(ventana, text="Complementaria para UI:").pack()
    tk.Label(ventana, bg=f"#{hex_comp}", text=f"{hex_comp}", fg="white").pack(fill="x")
    
    # --- Versiones análogas útiles para UI ---
    tk.Label(ventana, text="Colores Análogos para UI:").pack()
    for delta in [-0.08, 0.08]:
        h_analog = (h + delta) % 1.0
        r2, g2, b2 = colorsys.hls_to_rgb(h_analog, l, s)
        r2, g2, b2 = int(r2*255), int(g2*255), int(b2*255)
        hex_analog = rgb_a_hex(r2, g2, b2)
        # Ajustar fg según luminosidad
        fg_color = "black" if ((0.299*r2 + 0.587*g2 + 0.114*b2) > 186) else "white"
        tk.Label(ventana, bg=f"#{hex_analog}", text=f"{hex_analog}", fg=fg_color).pack(fill="x")





def generar_paletas_armonicas():
    hex_value = entrada.get()
    if len(hex_value) != 6:
        messagebox.showerror("Error", "Código hexadecimal inválido")
        return
    
    r = int(hex_value[0:2], 16)
    g = int(hex_value[2:4], 16)
    b = int(hex_value[4:6], 16)
    
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    
    # Ventana para mostrar paletas
    ventana = tk.Toplevel(root)
    ventana.title("Paletas Armónicas")
    
    # --- Complementaria ---
    h_complementaria = (h + 0.5) % 1.0
    r1, g1, b1 = colorsys.hls_to_rgb(h_complementaria, l, s)
    r1, g1, b1 = int(r1*255), int(g1*255), int(b1*255)
    hex_complementaria = rgb_a_hex(r1, g1, b1)
    
    tk.Label(ventana, text="Complementaria:").pack()
    tk.Label(ventana, bg=f"#{hex_value}", text=f"Original #{hex_value}", fg="white").pack(fill="x")
    tk.Label(ventana, bg=f"#{hex_complementaria}", text=f"Complementaria #{hex_complementaria}", fg="white").pack(fill="x")
    
    # --- Análoga ---
    tk.Label(ventana, text="Análoga:").pack()
    for delta in [-0.08, 0.08]:
        h_analog = (h + delta) % 1.0
        r2, g2, b2 = colorsys.hls_to_rgb(h_analog, l, s)
        r2, g2, b2 = int(r2*255), int(g2*255), int(b2*255)
        hex_analog = rgb_a_hex(r2, g2, b2)
        tk.Label(ventana, bg=f"#{hex_analog}", text=f"#{hex_analog}", fg="white").pack(fill="x")
    
    # --- Triádica ---
    tk.Label(ventana, text="Triádica:").pack()
    for delta in [1/3, 2/3]:
        h_tri = (h + delta) % 1.0
        r3, g3, b3 = colorsys.hls_to_rgb(h_tri, l, s)
        r3, g3, b3 = int(r3*255), int(g3*255), int(b3*255)
        hex_tri = rgb_a_hex(r3, g3, b3)
        tk.Label(ventana, bg=f"#{hex_tri}", text=f"#{hex_tri}", fg="white").pack(fill="x")
    
    # --- Tetrádica ---
    tk.Label(ventana, text="Tetrádica:").pack()
    for delta in [0.25, 0.5, 0.75]:
        h_tetra = (h + delta) % 1.0
        r4, g4, b4 = colorsys.hls_to_rgb(h_tetra, l, s)
        r4, g4, b4 = int(r4*255), int(g4*255), int(b4*255)
        hex_tetra = rgb_a_hex(r4, g4, b4)
        tk.Label(ventana, bg=f"#{hex_tetra}", text=f"#{hex_tetra}", fg="white").pack(fill="x")


# Funciones base
def generar_color_aleatorio():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return r, g, b

def rgb_a_hex(r, g, b):
    return f"{r:02X}{g:02X}{b:02X}"

def analizar_color(r, g, b):
    luminosidad = (0.299*r + 0.587*g + 0.114*b)
    claro_oscuro = "Claro" if luminosidad > 127 else "Oscuro"
    
    # Colores base
    colores_base = {
        "Rojo": (255,0,0),
        "Verde": (0,255,0),
        "Azul": (0,0,255),
        "Negro": (0,0,0),
        "Blanco": (255,255,255),
        "Marrón": (165,42,42),
        "Púrpura": (128,0,128),
        "Amarillo": (255,255,0),
        "Cian": (0,255,255),
        "Magenta": (255,0,255)
    }
    
    min_dist = float('inf')
    color_mas_cercano = ""
    for nombre, (cr, cg, cb) in colores_base.items():
        dist = ((r-cr)**2 + (g-cg)**2 + (b-cb)**2)**0.5
        if dist < min_dist:
            min_dist = dist
            color_mas_cercano = nombre
            
    return claro_oscuro, color_mas_cercano

def actualizar_canvas(r, g, b):
    hex_color = rgb_a_hex(r, g, b)
    canvas.config(bg=f"#{hex_color}")
    entrada.delete(0, tk.END)
    entrada.insert(0, hex_color)
    
    claro_oscuro, color_mas_cercano = analizar_color(r, g, b)
    info_label.config(text=f"{claro_oscuro}, se parece a {color_mas_cercano}")

def sliders_a_rgb():
    h = hue_slider.get() / 360
    l = light_slider.get() / 100
    s = sat_slider.get() / 100
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    r, g, b = int(r*255), int(g*255), int(b*255)
    actualizar_canvas(r, g, b)

def rgb_sliders():
    r, g, b = r_slider.get(), g_slider.get(), b_slider.get()
    actualizar_canvas(r, g, b)
    
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    hue_slider.set(h*360)
    light_slider.set(l*100)
    sat_slider.set(s*100)

def mostrar_color():
    hex_value = entrada.get()
    if len(hex_value) != 6:
        messagebox.showerror("Error", "Ingrese 6 caracteres hexadecimales (ej. FF5733)")
        return
    try:
        r = int(hex_value[0:2], 16)
        g = int(hex_value[2:4], 16)
        b = int(hex_value[4:6], 16)
        actualizar_canvas(r, g, b)
        
        r_slider.set(r)
        g_slider.set(g)
        b_slider.set(b)
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        hue_slider.set(h*360)
        light_slider.set(l*100)
        sat_slider.set(s*100)
        
    except ValueError:
        messagebox.showerror("Error", "Código hexadecimal inválido")

def randomizar():
    r, g, b = generar_color_aleatorio()
    actualizar_canvas(r, g, b)
    
    r_slider.set(r)
    g_slider.set(g)
    b_slider.set(b)
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    hue_slider.set(h*360)
    light_slider.set(l*100)
    sat_slider.set(s*100)

def guardar_imagen():
    hex_value = entrada.get()
    if len(hex_value) != 6:
        messagebox.showerror("Error", "Código hexadecimal inválido para guardar")
        return
    if not os.path.exists("muestras"):
        os.makedirs("muestras")
    img = Image.new("RGB", (200, 100), f"#{hex_value}")
    ruta = os.path.join("muestras", f"{hex_value}.png")
    img.save(ruta)
    messagebox.showinfo("Guardado", f"Imagen guardada en {ruta}")

# --- NUEVA FUNCION: Crear versiones en otros colores ---
def crear_versiones_colores():
    hex_value = entrada.get()
    if len(hex_value) != 6:
        messagebox.showerror("Error", "Código hexadecimal inválido")
        return
    r = int(hex_value[0:2], 16)
    g = int(hex_value[2:4], 16)
    b = int(hex_value[4:6], 16)
    
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    
    # Colores base a generar versiones
    colores_base_hue = {
        "Rojo": 0,
        "Amarillo": 60,
        "Verde": 120,
        "Cian": 180,
        "Azul": 240,
        "Magenta": 300,
        "Púrpura": 280,
        "Marrón": 30
    }
    
    ventana = tk.Toplevel(root)
    ventana.title("Versiones del color")
    
    for nombre, hue_grados in colores_base_hue.items():
        hue = hue_grados / 360
        r1, g1, b1 = colorsys.hls_to_rgb(hue, l, s)
        r1, g1, b1 = int(r1*255), int(g1*255), int(b1*255)
        color_hex = rgb_a_hex(r1, g1, b1)
        
        frame = tk.Frame(ventana, bg=f"#{color_hex}", width=100, height=50)
        frame.pack(padx=5, pady=5, fill="x")
        label = tk.Label(frame, text=f"{nombre}: #{color_hex}", bg=f"#{color_hex}", fg="white")
        label.pack()

# --- INTERFAZ ---
root = tk.Tk()
root.title("Editor de Color Hexadecimal")
root.geometry("400x600")

# Entrada de color
tk.Label(root, text="Código Hexadecimal:").pack()
entrada = tk.Entry(root, width=10, font=("Arial", 14))
entrada.pack()
tk.Button(root, text="Mostrar color", command=mostrar_color).pack(pady=5)
tk.Button(root, text="Randomizar", command=randomizar).pack(pady=5)
tk.Button(root, text="Guardar imagen", command=guardar_imagen).pack(pady=5)
tk.Button(root, text="Crear versiones en otros colores", command=crear_versiones_colores).pack(pady=5)
tk.Button(root, text="Generar paletas armónicas", command=generar_paletas_armonicas).pack(pady=5)
tk.Button(root, text="Paletas para interfaz", command=generar_paletas_interface).pack(pady=5)



# Canvas
canvas = tk.Canvas(root, width=200, height=100, bg="white")
canvas.pack(pady=10)

# Info de color
info_label = tk.Label(root, text="", font=("Arial", 10))
info_label.pack(pady=5)

# Sliders RGB
tk.Label(root, text="Editar RGB:").pack()
r_slider = tk.Scale(root, from_=0, to=255, orient="horizontal", label="R", command=lambda x: rgb_sliders())
r_slider.pack(fill="x")
g_slider = tk.Scale(root, from_=0, to=255, orient="horizontal", label="G", command=lambda x: rgb_sliders())
g_slider.pack(fill="x")
b_slider = tk.Scale(root, from_=0, to=255, orient="horizontal", label="B", command=lambda x: rgb_sliders())
b_slider.pack(fill="x")

# Sliders HSL
tk.Label(root, text="Editar HSL:").pack()
hue_slider = tk.Scale(root, from_=0, to=360, orient="horizontal", label="H", command=lambda x: sliders_a_rgb())
hue_slider.pack(fill="x")
light_slider = tk.Scale(root, from_=0, to=100, orient="horizontal", label="L", command=lambda x: sliders_a_rgb())
light_slider.pack(fill="x")
sat_slider = tk.Scale(root, from_=0, to=100, orient="horizontal", label="S", command=lambda x: sliders_a_rgb())
sat_slider.pack(fill="x")

# Inicializar
randomizar()

root.mainloop()
