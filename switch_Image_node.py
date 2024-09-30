import torch
from PIL import Image
import numpy as np
import os

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
                "source": (anyType, {}),  # Fuente de entrada única
                "storage_folder": ("STRING", {"default": "images_temp"}),  # Ruta de almacenamiento definida por el usuario
            }
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    RETURN_TYPES = (anyType,) * 10  # Hasta 10 salidas posibles
    RETURN_NAMES = tuple(f"SOURCE_{i}" for i in range(10))

    FUNCTION = "node"
    CATEGORY = "Custom Nodes"

    def node(self, condition, source, storage_folder):
        # Crear la carpeta de almacenamiento proporcionada por el usuario si no existe
        os.makedirs(storage_folder, exist_ok=True)

        # Validar que la condición esté dentro del rango permitido
        if 0 <= condition < 10:
            # Guardar la imagen en el disco
            self.save_image_to_disk(source, condition, storage_folder)

            # Crear una lista de salidas, cargando las imágenes desde el disco o creando un tensor transparente si no existen
            outputs = []
            for i in range(10):
                output_image = self.load_image_from_disk(i, source, storage_folder)
                outputs.append(output_image)

            return tuple(outputs)
        else:
            raise ValueError(f"Error: La condición {condition} está fuera del rango permitido (0-9).")

    def save_image_to_disk(self, tensor, condition, storage_folder):
        # Convertir el tensor a una imagen PIL y guardarlo como PNG
        image = self.tensor_to_pil(tensor)
        file_path = os.path.join(storage_folder, f"image_{condition}.png")
        image.save(file_path)

    def load_image_from_disk(self, condition, source_tensor, storage_folder):
        # Intentar cargar la imagen del disco
        file_path = os.path.join(storage_folder, f"image_{condition}.png")
        if os.path.exists(file_path):
            image = Image.open(file_path)
            return self.pil_to_tensor(image)
        else:
            # Si no existe la imagen, devolver un tensor transparente
            return self.create_transparent_tensor(source_tensor)

    def create_transparent_tensor(self, source_tensor):
        # Verificar si el tensor tiene 4 dimensiones
        if len(source_tensor.shape) == 4:
            _, height, width, _ = source_tensor.shape
            # Crear un tensor de ceros (transparente) con la misma forma que el tensor fuente
            transparent_tensor = torch.zeros((1, height, width, 4), dtype=torch.float32)
            return transparent_tensor
        else:
            raise ValueError(f"Error: El tensor fuente tiene una forma inesperada: {source_tensor.shape}")

    def tensor_to_pil(self, tensor):
        # Convertir tensor a imagen PIL (suponiendo que sea un tensor RGBA)
        array = tensor.squeeze().numpy()  # Eliminar dimensiones innecesarias
        array = (array * 255).astype(np.uint8)  # Convertir a entero 8 bits
        return Image.fromarray(array)

    def pil_to_tensor(self, image):
        # Convertir imagen PIL a tensor
        array = np.array(image).astype(np.float32) / 255.0  # Convertir de entero 8 bits a flotante
        tensor = torch.tensor(array).unsqueeze(0)  # Añadir dimensión batch
        return tensor
