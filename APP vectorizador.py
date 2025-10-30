import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import svgwrite

class ColorVectorizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vectorizador de Colores a SVG")
        self.root.geometry("1000x750")

        # Variables
        self.cv_image = None
        self.tk_img_orig = None
        self.tk_img_preview = None
        self.preview_image = None
        self.simplify_value = tk.DoubleVar(value=2.0)
        self.stroke_width = tk.IntVar(value=1)
        self.num_colors = tk.IntVar(value=8)
        self.invert_colors = tk.BooleanVar(value=False)
        self.black_and_white = tk.BooleanVar(value=False)
        self.gray_levels = tk.IntVar(value=2)

        # Panel de imágenes
        self.frame_images = tk.Frame(root)
        self.frame_images.pack(pady=10)

        tk.Label(self.frame_images, text="Original").grid(row=0, column=0)
        tk.Label(self.frame_images, text="Vista Previa").grid(row=0, column=1)

        self.img_label_orig = tk.Label(self.frame_images)
        self.img_label_orig.grid(row=1, column=0, padx=10)

        self.img_label_preview = tk.Label(self.frame_images)
        self.img_label_preview.grid(row=1, column=1, padx=10)

        # Panel de controles
        self.frame_controls = tk.Frame(root)
        self.frame_controls.pack(pady=10)

        tk.Button(self.frame_controls, text="Cargar Imagen", command=self.load_image, width=20).grid(row=0, column=0, padx=5)
        tk.Label(self.frame_controls, text="Colores:").grid(row=0, column=1)
        tk.Scale(self.frame_controls, from_=2, to=20, orient=tk.HORIZONTAL, variable=self.num_colors, command=self.update_preview).grid(row=0, column=2)

        tk.Label(self.frame_controls, text="Suavizado contorno:").grid(row=0, column=3)
        tk.Scale(self.frame_controls, from_=0, to=10, resolution=0.5, orient=tk.HORIZONTAL, variable=self.simplify_value, command=self.update_preview).grid(row=0, column=4)

        tk.Label(self.frame_controls, text="Grosor línea:").grid(row=0, column=5)
        tk.Scale(self.frame_controls, from_=1, to=10, orient=tk.HORIZONTAL, variable=self.stroke_width).grid(row=0, column=6)

        tk.Checkbutton(self.frame_controls, text="Invertir colores", variable=self.invert_colors, command=self.update_preview).grid(row=1, column=0, padx=5)
        tk.Checkbutton(self.frame_controls, text="Blanco y Negro", variable=self.black_and_white, command=self.update_preview).grid(row=1, column=1, padx=5)

        # Scroll de niveles de gris (solo visible cuando BN está activado)
        tk.Label(self.frame_controls, text="Niveles de gris:").grid(row=1, column=2)
        tk.Scale(self.frame_controls, from_=2, to=20, orient=tk.HORIZONTAL, variable=self.gray_levels, command=self.update_preview).grid(row=1, column=3)

        tk.Button(self.frame_controls, text="Guardar SVG", command=self.vectorize_image, width=20).grid(row=1, column=6, padx=5)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Imagenes", "*.png;*.jpg;*.jpeg")])
        if not path:
            return

        # Cargar imagen original
        self.cv_image = cv2.imread(path)
        img = Image.open(path)
        img.thumbnail((450, 400))
        self.tk_img_orig = ImageTk.PhotoImage(img)
        self.img_label_orig.config(image=self.tk_img_orig)

        self.update_preview()

    def update_preview(self, *args):
        if self.cv_image is None:
            return

        img_rgb = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2RGB)

        # Aplicar inversión si está marcada
        if self.invert_colors.get():
            img_rgb = 255 - img_rgb

        if self.black_and_white.get():
            # Convertir a escala de grises
            img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

            # Cuantizar a los niveles de gris seleccionados
            levels = self.gray_levels.get()
            img_gray_q = np.floor(img_gray / 256 * levels) * (256 // levels)
            img_gray_q = img_gray_q.astype(np.uint8)

            self.preview_image = img_gray_q
            img_preview = cv2.cvtColor(img_gray_q, cv2.COLOR_GRAY2RGB)
        else:
            # Reducir colores usando K-means
            Z = img_rgb.reshape((-1, 3))
            Z = np.float32(Z)

            K = self.num_colors.get()
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            _, labels, centers = cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

            centers = np.uint8(centers)
            segmented_data = centers[labels.flatten()]
            img_segmented = segmented_data.reshape(img_rgb.shape)

            # Convertir a gris para detectar contornos
            img_gray = cv2.cvtColor(img_segmented, cv2.COLOR_RGB2GRAY)
            _, img_bin = cv2.threshold(img_gray, 1, 255, cv2.THRESH_BINARY)
            self.preview_image = img_bin
            img_preview = img_segmented

        # Mostrar preview
        img_preview_resized = cv2.resize(img_preview, (450, 400))
        img_preview_pil = Image.fromarray(img_preview_resized)
        self.tk_img_preview = ImageTk.PhotoImage(img_preview_pil)
        self.img_label_preview.config(image=self.tk_img_preview)

    def vectorize_image(self):
        if self.cv_image is None or self.preview_image is None:
            messagebox.showwarning("Atención", "Primero carga y previsualiza una imagen")
            return

        img_bin = self.preview_image
        contours_data = cv2.findContours(img_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours_data[0] if len(contours_data) == 2 else contours_data[1]

        if not contours:
            messagebox.showwarning("Aviso", "No se detectaron contornos")
            return

        svg_filename = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG", "*.svg")])
        if not svg_filename:
            return

        dwg = svgwrite.Drawing(svg_filename, profile='tiny')

        for cnt in contours:
            epsilon = self.simplify_value.get()
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            mask = np.zeros(img_bin.shape, dtype=np.uint8)
            cv2.drawContours(mask, [cnt], -1, 255, -1)

            if self.black_and_white.get():
                # Color basado en el tono de gris promedio
                mean_gray = int(cv2.mean(img_bin, mask=mask)[0])
                color_hex = svgwrite.utils.rgb(mean_gray, mean_gray, mean_gray)
            else:
                mean_color = cv2.mean(self.cv_image, mask=mask)[:3]
                color_hex = svgwrite.utils.rgb(int(mean_color[2]), int(mean_color[1]), int(mean_color[0]))

            points = [(int(p[0][0]), int(p[0][1])) for p in approx]
            dwg.add(dwg.polygon(points, fill=color_hex, stroke='black', stroke_width=self.stroke_width.get()))

        dwg.save()
        messagebox.showinfo("Éxito", f"SVG guardado en:\n{svg_filename}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ColorVectorizerApp(root)
    root.mainloop()
