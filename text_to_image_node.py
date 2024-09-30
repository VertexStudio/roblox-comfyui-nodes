import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont
import random

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
                "bg_color": ("STRING", {"default": "#FFDDC1"})
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_text_image"
    CATEGORY = "Text Processing"

    def generate_text_image(self, text, image_width, image_height, text_color, border_color, bg_color):
        # Crear una nueva imagen con el fondo de color especificado
        image = Image.new("RGB", (image_width, image_height), bg_color)
        draw = ImageDraw.Draw(image)

        # Lista de fuentes posibles
        font_paths = [
            "arial.ttf",
            "arialbd.ttf",
            "times.ttf",
            "timesbd.ttf",
            "cour.ttf",
            "courbd.ttf",
            "verdana.ttf",
            "verdanab.ttf",
            "calibri.ttf",
            "calibrib.ttf",
            "georgia.ttf",
            "georgiab.ttf",
            "tahoma.ttf",
            "tahomabd.ttf"
        ]
        
        # Seleccionar una fuente aleatoria
        font_path = random.choice(font_paths)

        # Generar un tamaño de borde aleatorio entre 10 y 80
        border_size = random.randint(10, 80)

        # Espacio disponible para el texto (restar 10 píxeles a cada lado)
        available_width = image_width - 2 * (border_size + 10)

        # Ajustar el tamaño de la fuente dinámicamente para que el texto encaje en el ancho disponible
        font_size = 1  # Empezar con una fuente pequeña
        font = ImageFont.truetype(font_path, font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

        # Aumentar el tamaño de la fuente hasta que el texto encaje dentro del ancho disponible
        while text_width < available_width:
            font_size += 1
            font = ImageFont.truetype(font_path, font_size)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]

        # Reducir el tamaño de la fuente en caso de que se pase del ancho disponible
        while text_width > available_width and font_size > 10:
            font_size -= 1
            font = ImageFont.truetype(font_path, font_size)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]

        # Calcular la posición del texto centrado
        text_x = (image_width - text_width) // 2
        text_y = (image_height - font_size) // 2  # Centramos verticalmente

        # Dibujar el borde (si border_size es mayor que 0)
        if border_size > 0:
            # Calcular los límites del borde
            border_x0 = text_x - 10
            border_y0 = text_y - 10
            border_x1 = text_x + text_width + 10
            border_y1 = text_y + font_size + 10

            # Dibujar el rectángulo del borde
            draw.rectangle([border_x0, border_y0, border_x1, border_y1], fill=border_color)

        # Dibujar el texto principal
        draw.text((text_x, text_y), text, font=font, fill=text_color)

        # Convertir la imagen a un array NumPy y normalizar
        img_array = np.array(image).astype(np.float32) / 255.0  # Normalizar a [0, 1]

        # Añadir nueva dimensión para el lote y convertir a tensor
        combined_image_tensor = torch.tensor(img_array).unsqueeze(0)  # Añadir nueva dimensión

        # Retornar la imagen generada como tensor
        return (combined_image_tensor,)
