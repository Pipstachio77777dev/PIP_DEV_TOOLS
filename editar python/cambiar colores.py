import tkinter as tk
from tkinter import filedialog, messagebox
import re
from colorsys import rgb_to_hls, hls_to_rgb

# Lista de nombres de colores estándar en CSS
NAMED_COLORS = {
    "black": "#000000", "white": "#ffffff", "red": "#ff0000", 
    "green": "#008000", "blue": "#0000ff", "yellow": "#ffff00", 
    "cyan": "#00ffff", "magenta": "#ff00ff", "gray": "#808080"
}

HEX_PATTERN = re.compile(r'#(?:[0-9a-fA-F]{3}){1,2}\b')
NAMED_PATTERN = re.compile(r'\b(' + '|'.join(NAMED_COLORS.keys()) + r')\b', re.IGNORECASE)

class ColorViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Colores Hex y Named")
        
        self.colors = []
        self.file_path = None
        self.file_content = ""
        
        # Botón abrir archivo
        tk.Button(root, text="Abrir archivo", command=self.open_file).pack(pady=5)
        
        # Listbox de colores (solo lectura)
        self.listbox = tk.Listbox(root, width=30)
        self.listbox.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        self.listbox.bind("<<ListboxSelect>>", self.show_color_preview)
        
        # Canvas para vista previa
        self.preview = tk.Canvas(root, width=100, height=100, bg="white")
        self.preview.pack(pady=10)
        
        # Input para mostrar color seleccionado
        self.color_entry = tk.Entry(root)
        self.color_entry.pack(pady=5)
        
        # Sliders H, L, S (solo visualización)
        self.hue_scale = tk.Scale(root, from_=0, to=360, label="Hue", orient=tk.HORIZONTAL, command=self.update_preview)
        self.hue_scale.pack(fill=tk.X, padx=5)
        self.light_scale = tk.Scale(root, from_=0, to=100, label="Lightness", orient=tk.HORIZONTAL, command=self.update_preview)
        self.light_scale.pack(fill=tk.X, padx=5)
        self.sat_scale = tk.Scale(root, from_=0, to=100, label="Saturation", orient=tk.HORIZONTAL, command=self.update_preview)
        self.sat_scale.pack(fill=tk.X, padx=5)
        
        self.current_rgb = (0,0,0)
    
    def open_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Python/TSX files", "*.py *.tsx")])
        if not self.file_path:
            return
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.file_content = f.read()
        hex_colors = HEX_PATTERN.findall(self.file_content)
        named_colors = NAMED_PATTERN.findall(self.file_content)
        named_colors = [NAMED_COLORS[c.lower()] for c in named_colors]
        self.colors = list(set(hex_colors + named_colors))
        self.listbox.delete(0, tk.END)
        for c in self.colors:
            self.listbox.insert(tk.END, c)
    
    def show_color_preview(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        color = self.colors[selection[0]]
        self.preview.config(bg=color)
        self.current_rgb = self.hex_to_rgb(color)
        # Actualizar sliders según el color seleccionado
        h,l,s = rgb_to_hls(*[x/255 for x in self.current_rgb])
        self.hue_scale.set(int(h*360))
        self.light_scale.set(int(l*100))
        self.sat_scale.set(int(s*100))
        # Mostrar el color en el entry
        self.color_entry.delete(0, tk.END)
        self.color_entry.insert(0, color)
    
    def update_preview(self, event):
        """Actualiza solo la vista previa y el entry, sin modificar la lista"""
        h = self.hue_scale.get()/360
        l = self.light_scale.get()/100
        s = self.sat_scale.get()/100
        r,g,b = hls_to_rgb(h,l,s)
        rgb = (int(r*255), int(g*255), int(b*255))
        hex_color = self.rgb_to_hex(rgb)
        self.preview.config(bg=hex_color)
        self.color_entry.delete(0, tk.END)
        self.color_entry.insert(0, hex_color)
    
    @staticmethod
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join([c*2 for c in hex_color])
        r = int(hex_color[0:2],16)
        g = int(hex_color[2:4],16)
        b = int(hex_color[4:6],16)
        return (r,g,b)
    
    @staticmethod
    def rgb_to_hex(rgb):
        return "#%02x%02x%02x" % rgb

root = tk.Tk()
app = ColorViewer(root)
root.mainloop()
