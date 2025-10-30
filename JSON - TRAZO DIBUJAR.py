import tkinter as tk
from tkinter import filedialog, messagebox
import json
import requests
import xml.etree.ElementTree as ET
import math
import re

KANJIVG_BASE_URL = "https://raw.githubusercontent.com/KanjiVG/kanjivg/master/kanji"

def kanji_to_unicode_hex(kanji):
    return f"{ord(kanji):05x}"

def fetch_kanji_svg(kanji):
    hex_code = kanji_to_unicode_hex(kanji)
    url = f"{KANJIVG_BASE_URL}/{hex_code}.svg"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error al descargar SVG para {kanji}: {e}")
        return None

def extract_paths_from_svg(svg_content):
    try:
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        root = ET.fromstring(svg_content)
        paths = root.findall('.//svg:path', ns)
        d_list = [path.attrib['d'] for path in paths if 'd' in path.attrib]
        return d_list
    except ET.ParseError as e:
        print(f"Error al parsear SVG: {e}")
        return []

def lerp(a, b, t):
    return a + (b - a) * t

def cubic_bezier(p0, p1, p2, p3, t):
    """ Calcula un punto en curva Bézier cúbica en t (0-1) """
    x = (1 - t)**3 * p0[0] + 3 * (1 - t)**2 * t * p1[0] + 3 * (1 - t) * t**2 * p2[0] + t**3 * p3[0]
    y = (1 - t)**3 * p0[1] + 3 * (1 - t)**2 * t * p1[1] + 3 * (1 - t) * t**2 * p2[1] + t**3 * p3[1]
    return (x, y)

def sample_points_from_d(d_attr, num_points=50):
    """
    Parse básico para extraer y muestrear puntos de comandos M, L y C (Bezier cúbica) del atributo d.
    Se maneja mayúsculas (absoluto) y minúsculas (relativo).
    """
    tokens = re.findall(r'[MLCmlcZz]|-?[\d.]+(?:e-?\d+)?', d_attr)
    points = []
    idx = 0
    current_pos = (0, 0)
    start_subpath = (0, 0)  # para 'Z' o 'z'

    while idx < len(tokens):
        cmd = tokens[idx]
        idx += 1
        is_relative = cmd.islower()
        cmd = cmd.upper()

        if cmd == 'M':
            # M x y (move to)
            x = float(tokens[idx])
            y = float(tokens[idx+1])
            idx += 2
            if is_relative:
                x += current_pos[0]
                y += current_pos[1]
            current_pos = (x, y)
            start_subpath = current_pos
            points.append(current_pos)

        elif cmd == 'L':
            # L x y (line to)
            x = float(tokens[idx])
            y = float(tokens[idx+1])
            idx += 2
            if is_relative:
                x += current_pos[0]
                y += current_pos[1]
            p0 = current_pos
            p1 = (x, y)
            # Muestrear línea con num_points intervalos pero solo puntos intermedios (evitar duplicados)
            for i in range(1, num_points + 1):
                t = i / num_points
                xt = lerp(p0[0], p1[0], t)
                yt = lerp(p0[1], p1[1], t)
                points.append((xt, yt))
            current_pos = p1

        elif cmd == 'C':
            # C x1 y1 x2 y2 x y (curva Bézier cúbica)
            x1 = float(tokens[idx])
            y1 = float(tokens[idx+1])
            x2 = float(tokens[idx+2])
            y2 = float(tokens[idx+3])
            x = float(tokens[idx+4])
            y = float(tokens[idx+5])
            idx += 6
            if is_relative:
                x1 += current_pos[0]
                y1 += current_pos[1]
                x2 += current_pos[0]
                y2 += current_pos[1]
                x += current_pos[0]
                y += current_pos[1]

            p0 = current_pos
            p1 = (x1, y1)
            p2 = (x2, y2)
            p3 = (x, y)

            # Muestrear curva Bézier (evitando duplicar p0)
            for i in range(1, num_points + 1):
                t = i / num_points
                pt = cubic_bezier(p0, p1, p2, p3, t)
                points.append(pt)
            current_pos = p3

        elif cmd == 'Z':
            # Close path (línea al punto de inicio del subpath)
            p0 = current_pos
            p1 = start_subpath
            for i in range(1, num_points + 1):
                t = i / num_points
                xt = lerp(p0[0], p1[0], t)
                yt = lerp(p0[1], p1[1], t)
                points.append((xt, yt))
            current_pos = p1

        else:
            # Ignorar otros comandos
            pass

    return points

def distance_point_to_path(point, path_points):
    min_dist = float('inf')
    px, py = point

    for i in range(len(path_points) - 1):
        x1, y1 = path_points[i]
        x2, y2 = path_points[i + 1]

        dx = x2 - x1
        dy = y2 - y1

        if dx == dy == 0:
            dist = math.hypot(px - x1, py - y1)
        else:
            t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
            proj_x = x1 + t * dx
            proj_y = y1 + t * dy
            dist = math.hypot(px - proj_x, py - proj_y)

        if dist < min_dist:
            min_dist = dist
    return min_dist

class KanjiViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visor y Pizarra de Kanji")

        self.kanji_data = []
        self.current_index = 0

        self.index_label = tk.Label(root, text="", font=("Arial", 16))
        self.index_label.pack(pady=5)

        self.kanji_label = tk.Label(root, text="", font=("Arial", 100))
        self.kanji_label.pack(pady=5)

        button_frame = tk.Frame(root)
        button_frame.pack()

        self.prev_button = tk.Button(button_frame, text="← Anterior", command=self.prev_kanji, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=10)

        self.next_button = tk.Button(button_frame, text="Siguiente →", command=self.next_kanji, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=10)

        self.load_button = tk.Button(root, text="Cargar JSON", command=self.load_json)
        self.load_button.pack(pady=10)

        self.canvas_width = 400
        self.canvas_height = 400
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(pady=10)

        control_frame = tk.Frame(root)
        control_frame.pack()

        self.clear_button = tk.Button(control_frame, text="Limpiar trazo", command=self.clear_drawing, state=tk.DISABLED)
        self.clear_button.pack(side=tk.LEFT, padx=10)

        self.check_button = tk.Button(control_frame, text="Validar trazo", command=self.check_drawing, state=tk.DISABLED)
        self.check_button.pack(side=tk.LEFT, padx=10)

        self.drawing = False
        self.user_points = []
        self.kanji_paths = []
        self.current_scale = 1.0
        self.current_offset = (0, 0)

        self.canvas.bind("<ButtonPress-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw_motion)
        self.canvas.bind("<ButtonRelease-1>", self.end_drawing)

    def load_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")])
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            self.kanji_data = []
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "kanji" in item:
                        self.kanji_data.append(item["kanji"])

            if not self.kanji_data:
                messagebox.showerror("Error", "No se encontraron kanjis válidos en el JSON.")
                return

            self.current_index = 0
            self.update_display()
            self.update_buttons()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")

    def update_display(self):
        kanji = self.kanji_data[self.current_index]
        total = len(self.kanji_data)
        self.index_label.config(text=f"Kanji {self.current_index + 1} de {total}")
        self.kanji_label.config(text=kanji)

        self.load_and_draw_kanji_paths(kanji)

        self.clear_button.config(state=tk.NORMAL)
        self.check_button.config(state=tk.NORMAL)
        self.clear_drawing()

    def update_buttons(self):
        total = len(self.kanji_data)
        self.prev_button.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_index < total - 1 else tk.DISABLED)

    def next_kanji(self):
        if self.current_index < len(self.kanji_data) - 1:
            self.current_index += 1
            self.update_display()
            self.update_buttons()

    def prev_kanji(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()
            self.update_buttons()

    def load_and_draw_kanji_paths(self, kanji):
        svg_content = fetch_kanji_svg(kanji)
        if not svg_content:
            messagebox.showerror("Error", "No se pudo obtener el SVG del kanji.")
            self.kanji_paths = []
            self.canvas.delete("all")
            return

        d_list = extract_paths_from_svg(svg_content)
        self.kanji_paths = []
        all_points = []
        for d in d_list:
            pts = sample_points_from_d(d, num_points=100)
            if len(pts) > 1:
                self.kanji_paths.append(pts)
                all_points.extend(pts)

        if not all_points:
            messagebox.showerror("Error", "No se encontraron puntos para los trazos del kanji.")
            self.canvas.delete("all")
            return

        xs = [p[0] for p in all_points]
        ys = [p[1] for p in all_points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        w_svg = max_x - min_x
        h_svg = max_y - min_y

        scale_x = (self.canvas_width - 40) / w_svg
        scale_y = (self.canvas_height - 40) / h_svg
        self.current_scale = min(scale_x, scale_y)

        offset_x = (self.canvas_width - w_svg * self.current_scale) / 2
        offset_y = (self.canvas_height - h_svg * self.current_scale) / 2
        self.current_offset = (offset_x - min_x * self.current_scale, offset_y - min_y * self.current_scale)

        self.canvas.delete("all")
        for pts in self.kanji_paths:
            scaled = [self.transform_point(p) for p in pts]
            # Línea guía más gruesa
            self.canvas.create_line(scaled, fill="lightgray", width=8, smooth=True)

    def transform_point(self, point):
        x, y = point
        ox, oy = self.current_offset
        sx = x * self.current_scale + ox
        sy = y * self.current_scale + oy
        return (sx, sy)

    def start_drawing(self, event):
        self.drawing = True
        self.user_points = [(event.x, event.y)]
        self.last_x, self.last_y = event.x, event.y

    def draw_motion(self, event):
        if self.drawing:
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y, fill="blue", width=3, capstyle=tk.ROUND, tags="user_line", smooth=True)
            self.user_points.append((event.x, event.y))
            self.last_x, self.last_y = event.x, event.y

    def end_drawing(self, event):
        self.drawing = False

    def clear_drawing(self):
        self.canvas.delete("user_line")
        self.user_points = []
        self.canvas.delete("all")
        for pts in self.kanji_paths:
            scaled = [self.transform_point(p) for p in pts]
            self.canvas.create_line(scaled, fill="lightgray", width=8, smooth=True)

    def check_drawing(self):
        if not self.user_points:
            messagebox.showinfo("Validación", "Por favor, dibuja el kanji primero.")
            return

        threshold = 15  # tolerancia en pixeles
        correct_points = 0

        all_path_points = []
        for pts in self.kanji_paths:
            all_path_points.extend([self.transform_point(p) for p in pts])

        if not all_path_points:
            messagebox.showerror("Error", "No hay trazos originales para comparar.")
            return

        for p in self.user_points:
            dist = distance_point_to_path(p, all_path_points)
            if dist <= threshold:
                correct_points += 1

        ratio = correct_points / len(self.user_points)
        if ratio > 0.7:
            messagebox.showinfo("Resultado", f"¡Buen trabajo! Precisión: {ratio:.2%}")
        else:
            messagebox.showinfo("Resultado", f"Intento insuficiente. Precisión: {ratio:.2%}")

if __name__ == "__main__":
    root = tk.Tk()
    app = KanjiViewerApp(root)
    root.mainloop()