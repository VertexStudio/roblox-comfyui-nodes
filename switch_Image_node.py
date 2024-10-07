import torch
from PIL import Image
import numpy as np
import os
import folder_paths

class AnyType_fill(str):
    def __ne__(self, __value: object) -> bool:
        return False

# Nuestro instancia anyType quiere ser una cadena comodín
anyType = AnyType_fill("*")

class SwitchImageNode:
    def __init__(self):
        self.Started = 0
        self.switch = 0
        self.mode = 0

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": ("INT", {"default": 0, "min": 0, "max": 9, "step": 1}),  # Entero para decidir la salida
                "source_folder": ("STRING", {"default": "input/Liveries/Stickers"}),  # Carpeta de origen
            }
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    RETURN_TYPES = (anyType,) * 10  # Hasta 10 salidas posibles
    RETURN_NAMES = tuple(f"SOURCE_{i}" for i in range(10))

    FUNCTION = "node"
    CATEGORY = "Custom Nodes"

    def node(self, condition, source_folder):
        # Base directory for relative paths (ComfyUI base folder + source)
        source_base_dir = os.path.join(folder_paths.get_input_directory(), source_folder)

        # Validar que la condición esté dentro del rango permitido
        if 0 <= condition < 10:
            # Crear una lista de salidas, cargando las imágenes desde el disco secuencialmente
            outputs = []
            for i in range(10):
                output_image = self.load_image_from_disk(i, source_base_dir)
                outputs.append(output_image)

            return tuple(outputs)
        else:
            raise ValueError(f"Error: La condición {condition} está fuera del rango permitido (0-9).")

    def load_image_from_disk(self, condition, source_folder):
        # Formato secuencial basado en el nombre del archivo (image_00001_.png, image_00002_.png, etc.)
        file_name = f"image_{(condition + 1):05d}.png"
        file_path = os.path.join(source_folder, file_name)

        if os.path.exists(file_path):
            # Cargar la imagen desde la carpeta de origen
            image = Image.open(file_path)
            return self.pil_to_tensor(image)
        else:
            # Si no existe la imagen, devolver un tensor transparente
            return self.create_transparent_tensor()

    def create_transparent_tensor(self):
        # Crear un tensor transparente predeterminado (1x256x256x4)
        transparent_tensor = torch.zeros((1, 256, 256, 4), dtype=torch.float32)
        return transparent_tensor

    def pil_to_tensor(self, image):
        # Convertir imagen PIL a tensor
        array = np.array(image).astype(np.float32) / 255.0  # Convertir de entero 8 bits a flotante
        tensor = torch.tensor(array).unsqueeze(0)  # Añadir dimensión batch
        return tensor
