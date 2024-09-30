import torch
import numpy as np
from PIL import Image

class MirrorEffectNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "axis": ("INT", {"default": 0, "options": [0, 1]}),  # 0 para horizontal, 1 para vertical
                "percentage": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),  # Porcentaje donde empieza el espejo
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_mirror_effect"
    CATEGORY = "Image Processing"

    def apply_mirror_effect(self, image, axis, percentage):
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

        # Obtener el tamaño de la imagen
        width, height = pil_image.size

        # Calcular el punto de corte basado en el porcentaje
        cut_x = int(width * percentage) if axis == 0 else width
        cut_y = int(height * percentage) if axis == 1 else height

        # Crear una imagen en blanco del mismo tamaño que la original
        result_image = pil_image.copy()

        # Reflejar la parte superior (o izquierda) en el eje indicado
        if axis == 0:  # Reflejo horizontal (izquierda a derecha)
            left_part = pil_image.crop((0, 0, cut_x, height))  # Parte izquierda de la imagen
            flipped_part = left_part.transpose(Image.FLIP_LEFT_RIGHT)  # Reflejo de la parte izquierda
            result_image.paste(flipped_part, (cut_x, 0))  # Pegar el reflejo en el punto de corte
        elif axis == 1:  # Reflejo vertical (arriba a abajo)
            top_part = pil_image.crop((0, 0, width, cut_y))  # Parte superior de la imagen
            flipped_part = top_part.transpose(Image.FLIP_TOP_BOTTOM)  # Reflejo de la parte superior
            result_image.paste(flipped_part, (0, cut_y))  # Pegar el reflejo en el punto de corte

        # Convertir la imagen combinada de vuelta a matriz NumPy y normalizar a [0, 1]
        result_image_np = np.array(result_image).astype(np.float32) / 255.0

        # Añadir de nuevo la dimensión de lote y convertir a tensor
        result_image_tensor = torch.tensor(result_image_np).unsqueeze(0)

        return (result_image_tensor,)
