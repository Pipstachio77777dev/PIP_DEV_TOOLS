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

def average_distance_between_paths(user_points, kanji_paths):
    """Calcula la distancia promedio mínima de cada punto del usuario al kanji."""
    # Aplanar puntos kanji y aplicar transformación para que estén en coordenadas canvas
    all_kanji_points = []
    for path in kanji_paths:
        all_kanji_points.extend(path)

    min_dists = []
    for up in user_points:
        dist = distance_point_to_path(up, all_kanji_points)
        min_dists.append(dist)
    if min_dists:
        return sum(min_dists) / len(min_dists)
    else:
        return float('inf')

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

        self.animate_button = tk.Button(root, text="Mostrar Animación", command=self.animate_kanji, state=tk.DISABLED)
        self.animate_button.pack(pady=5)

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

        # Variables para animación
        self.animation_index = 0
        self.animation_points_scaled = []
        self.animation_line_ids = []

    def load_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")])
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, list):
                messagebox.showerror("Error", "El JSON debe contener una lista de kanjis.")
                return
            self.kanji_data = data
            self.current_index = 0
            self.show_kanji()
            self.prev_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.NORMAL)
            self.animate_button.config(state=tk.NORMAL)
            self.clear_button.config(state=tk.NORMAL)
            self.check_button.config(state=tk.NORMAL)
            self.user_points.clear()
            self.clear_canvas()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo JSON: {e}")

    def show_kanji(self):
        if not self.kanji_data:
            return

        kanji_info = self.kanji_data[self.current_index]
        kanji_char = kanji_info.get("kanji", "?")
        self.kanji_label.config(text=kanji_char)
        self.index_label.config(text=f"Kanji {self.current_index + 1} de {len(self.kanji_data)}")

        # Descargar y preparar paths SVG
        svg_content = fetch_kanji_svg(kanji_char)
        if svg_content:
            d_paths = extract_paths_from_svg(svg_content)
            self.kanji_paths = [sample_points_from_d(d) for d in d_paths]
            self.scale_and_center_paths()
            self.clear_canvas()
            self.draw_kanji_paths()
        else:
            self.kanji_paths = []
            self.clear_canvas()

        self.user_points.clear()

    def scale_and_center_paths(self):
        # Calcular bbox total de todos los paths
        all_points = [pt for path in self.kanji_paths for pt in path]
        if not all_points:
            return
        xs = [p[0] for p in all_points]
        ys = [p[1] for p in all_points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        kanji_width = max_x - min_x
        kanji_height = max_y - min_y

        scale_x = (self.canvas_width * 0.8) / kanji_width
        scale_y = (self.canvas_height * 0.8) / kanji_height
        self.current_scale = min(scale_x, scale_y)

        offset_x = (self.canvas_width - kanji_width * self.current_scale) / 2 - min_x * self.current_scale
        offset_y = (self.canvas_height - kanji_height * self.current_scale) / 2 - min_y * self.current_scale

        self.current_offset = (offset_x, offset_y)

        # Aplicar escala y offset a todos los paths
        new_paths = []
        for path in self.kanji_paths:
            new_path = [(p[0] * self.current_scale + offset_x, p[1] * self.current_scale + offset_y) for p in path]
            new_paths.append(new_path)
        self.kanji_paths = new_paths

    def draw_kanji_paths(self):
        for path in self.kanji_paths:
            for i in range(len(path) - 1):
                self.canvas.create_line(path[i][0], path[i][1], path[i+1][0], path[i+1][1], fill="black", width=3)

    def clear_canvas(self):
        self.canvas.delete("all")
        self.draw_kanji_paths()
        # No redibujar trazo usuario para limpiar bien

    def prev_kanji(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_kanji()

    def next_kanji(self):
        if self.current_index < len(self.kanji_data) - 1:
            self.current_index += 1
            self.show_kanji()

    def start_drawing(self, event):
        self.drawing = True
        self.user_points.append((event.x, event.y))
        # NO limpiar canvas al iniciar nuevo trazo

    def draw_motion(self, event):
        if self.drawing:
            last_point = self.user_points[-1]
            new_point = (event.x, event.y)
            self.user_points.append(new_point)
            self.canvas.create_line(last_point[0], last_point[1], new_point[0], new_point[1], fill="blue", width=4)

    def end_drawing(self, event):
        self.drawing = False

    def clear_drawing(self):
        self.user_points.clear()
        self.clear_canvas()

    def check_drawing(self):
        if not self.user_points:
            messagebox.showinfo("Validación", "No has dibujado nada.")
            return
        if not self.kanji_paths:
            messagebox.showinfo("Validación", "No hay un kanji cargado para comparar.")
            return

        avg_dist = average_distance_between_paths(self.user_points, self.kanji_paths)
        threshold = 60  # Umbral más permisivo para aceptar trazos más gruesos y sueltos

        if avg_dist < threshold:
            messagebox.showinfo("Validación", f"¡Buen trabajo! Tu trazo coincide con el kanji.\nDistancia promedio: {avg_dist:.2f}")
        else:
            messagebox.showinfo("Validación", f"No coincide bien con el kanji.\nDistancia promedio: {avg_dist:.2f}. Sigue practicando.")

    def animate_kanji(self):
        if not self.kanji_paths:
            return
        self.clear_canvas()
        # Animar sólo el primer trazo por simplicidad
        self.animation_points_scaled = self.kanji_paths[0]
        self.animation_index = 0
        # Borrar líneas previas de animación
        for line_id in self.animation_line_ids:
            self.canvas.delete(line_id)
        self.animation_line_ids.clear()
        self.animate_step()

    def animate_step(self):
        if self.animation_index >= len(self.animation_points_scaled) - 1:
            return
        # Dibujar línea acumulativa: de 0 a animation_index+1
        if self.animation_index == 0:
            # Primer segmento
            line_id = self.canvas.create_line(
                self.animation_points_scaled[0][0], self.animation_points_scaled[0][1],
                self.animation_points_scaled[1][0], self.animation_points_scaled[1][1],
                fill="red", width=5)
            self.animation_line_ids.append(line_id)
        else:
            # Dibujar segmento siguiente y acumularlo
            p1 = self.animation_points_scaled[self.animation_index]
            p2 = self.animation_points_scaled[self.animation_index + 1]
            line_id = self.canvas.create_line(
                p1[0], p1[1], p2[0], p2[1],
                fill="red", width=5)
            self.animation_line_ids.append(line_id)

        self.animation_index += 1
        self.root.after(30, self.animate_step)

if __name__ == "__main__":
    root = tk.Tk()
    app = KanjiViewerApp(root)
    root.mainloop()
