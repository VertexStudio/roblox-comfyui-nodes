import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont
import random
import os

class TextToImageNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING",),
                "image_width": ("INT", {"default": 512, "min": 100, "max": 2048, "step": 10}),
                "image_height": ("INT", {"default": 512, "min": 100, "max": 2048, "step": 10}),
                "text_color": ("STRING", {"default": "#000000"}),
                "border_color": ("STRING", {"default": "#FFFFFF"}),
                "bg_color": ("STRING", {"default": "#FFDDC1"}),
                "font_path": ("STRING", {"default": ""})
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_text_image"
    CATEGORY = "Text Processing"

    def generate_text_image(self, text, image_width, image_height, text_color, border_color, bg_color, font_path):
        # Crear una nueva imagen con el fondo de color especificado
        image = Image.new("RGB", (image_width, image_height), bg_color)
        draw = ImageDraw.Draw(image)

        # Usar una fuente predeterminada si no se proporciona una ruta de fuente válida
        if not font_path or not os.path.isfile(font_path):
            font = ImageFont.load_default()
        else:
            try:
                font = ImageFont.truetype(font_path, 12)  # Tamaño inicial arbitrario
            except IOError:
                print(f"No se pudo cargar la fuente desde {font_path}. Usando la fuente predeterminada.")
                font = ImageFont.load_default()

        # Generar un tamaño de borde aleatorio entre 10 y 80
        border_size = random.randint(10, 80)

        # Espacio disponible para el texto (restar 10 píxeles a cada lado)
        available_width = image_width - 2 * (border_size + 10)

        # Ajustar el tamaño de la fuente dinámicamente
        font_size = 1
        while True:
            font = font.font_variant(size=font_size)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            if text_width > available_width or font_size > 200:
                font_size -= 1
                font = font.font_variant(size=font_size)
                break
            font_size += 1

        # Calcular la posición del texto centrado
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (image_width - text_width) // 2
        text_y = (image_height - text_height) // 2

        # Dibujar el borde (si border_size es mayor que 0)
        if border_size > 0:
            border_x0 = text_x - 10
            border_y0 = text_y - 10
            border_x1 = text_x + text_width + 10
            border_y1 = text_y + text_height + 10
            draw.rectangle([border_x0, border_y0, border_x1, border_y1], fill=border_color)

        # Dibujar el texto principal
        draw.text((text_x, text_y), text, font=font, fill=text_color)

        # Convertir la imagen a un array NumPy y normalizar
        img_array = np.array(image).astype(np.float32) / 255.0

        # Añadir nueva dimensión para el lote y convertir a tensor
        combined_image_tensor = torch.tensor(img_array).unsqueeze(0)

        return (combined_image_tensor,)
