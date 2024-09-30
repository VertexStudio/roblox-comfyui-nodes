import torch
import numpy as np
from PIL import Image

class ScaleImageNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "background_image": ("IMAGE", {"default": None}),
                "scale_x": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "scale_y": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "position_x": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "position_y": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "rotation_angle": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 360.0, "step": 1.0}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "scale_image"
    CATEGORY = "Roblox"

    def scale_image(self, image, background_image, scale_x, scale_y, position_x, position_y, rotation_angle):
        # Convertir la imagen principal de tensor a matriz NumPy
        if isinstance(image, torch.Tensor):
            image = image.squeeze().cpu().numpy()  # Asegurarse de que el tensor esté en CPU y comprimido

        # Verificar los canales y convertir a RGBA si es necesario
        if image.shape[-1] == 3:
            # Crear un canal alfa basado en la intensidad de los píxeles, manteniendo opacos los píxeles de la imagen
            alpha_channel = np.where(np.sum(image, axis=-1, keepdims=True) > 0, 1.0, 0.0)
            image = np.concatenate((image, alpha_channel), axis=-1)
        elif image.shape[-1] == 4:
            # Mantener el canal alfa de la imagen si ya tiene 4 canales
            image[..., 3] = np.where(image[..., 3] > 0, 1.0, 0.0)  # Asegurar que el canal alfa sea 0 o 1
        else:
            raise ValueError(f"Se esperaba una imagen con 3 o 4 canales, pero tiene {image.shape[-1]}.")

        # Convertir la imagen principal a PIL
        pil_image = Image.fromarray((image * 255).astype(np.uint8), mode='RGBA')

        # Aplicar el escalado a la imagen principal
        width, height = pil_image.size
        new_width = int(width * scale_x)
        new_height = int(height * scale_y)
        scaled_image = pil_image.resize((new_width, new_height), Image.LANCZOS)  # Usar LANCZOS en lugar de ANTIALIAS

        # Aplicar la rotación
        rotated_image = scaled_image.rotate(rotation_angle, expand=True)

        # Convertir la imagen de fondo a PIL sin cambiar su tamaño
        if background_image is not None:
            if isinstance(background_image, torch.Tensor):
                background_image = background_image.squeeze().cpu().numpy()  # Comprimir y enviar a CPU

            if background_image.shape[-1] == 3:
                background_image = np.concatenate((background_image, np.ones((background_image.shape[0], background_image.shape[1], 1), dtype=np.float32)), axis=-1)
            elif background_image.shape[-1] != 4:
                raise ValueError(f"Se esperaba una imagen de fondo con 3 o 4 canales, pero tiene {background_image.shape[-1]}.")

            pil_background_image = Image.fromarray((background_image * 255).astype(np.uint8), mode='RGBA')
        else:
            raise ValueError("Se requiere una imagen de fondo válida.")

        # Asegurarse de que la imagen de fondo sea más grande que la imagen escalada y rotada
        bg_width, bg_height = pil_background_image.size

        # Calcular las coordenadas de posición basadas en valores proporcionados (relativo a la imagen de fondo)
        offset_x = int((bg_width - rotated_image.size[0]) * position_x)
        offset_y = int((bg_height - rotated_image.size[1]) * position_y)

        # Componer la imagen escalada y rotada sobre la imagen de fondo
        combined_image = pil_background_image.copy()
        combined_image.paste(rotated_image, (offset_x, offset_y), rotated_image)

        # Convertir la imagen combinada de vuelta a matriz NumPy y normalizar a [0, 1]
        combined_image_np = np.array(combined_image).astype(np.float32) / 255.0

        # Añadir de nuevo la dimensión de lote y convertir a tensor
        combined_image_tensor = torch.tensor(combined_image_np).unsqueeze(0)

        return (combined_image_tensor,)