import os
import json
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from comfy.cli_args import args
import folder_paths

class SaveImageNode:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_number_padding": ("STRING", {"default": "1"}),  # Padding como entrada de texto
                "filename_prefix": ("STRING", {"default": "image"}),
                "filename_delimiter": ("STRING", {"default": "_"}),  # Delimitador para el nombre de archivo
                "save_path": ("STRING", {"default": "images/output"}),  # Ruta de guardado como entrada
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("IMAGE",)  # Define que este nodo devuelve un tipo de imagen
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "image"

    def generate_unique_filename(self, save_path, filename_prefix, padding_length, filename_delimiter, starting_number):
        """Generar un nombre de archivo único que no sobrescriba imágenes existentes."""
        counter = starting_number  # Comienza desde el número especificado
        while True:
            # Generar el número del archivo con padding
            number_str = str(counter).zfill(padding_length)  # Aplicar padding
            file = f"{filename_prefix}{filename_delimiter}{number_str}.png"  # Nombre del archivo
            full_path = os.path.join(save_path, file)  # Ruta completa del archivo

            # Verificar si el archivo ya existe en la carpeta designada
            if not os.path.isfile(full_path):  # Verifica solo en la carpeta
                return full_path  # Retornar el nombre único si no existe

            counter += 1  # Incrementar el contador y continuar buscando

    def save_images(self, images, filename_number_padding="1", filename_prefix="image", 
                    filename_delimiter="_", save_path="images/output", prompt=None, extra_pnginfo=None):
        # Convertir el padding de cadena a entero
        try:
            padding_length = int(filename_number_padding)  # Convertir a entero
        except ValueError:
            padding_length = 1  # Valor predeterminado en caso de error de conversión

        # Crear la carpeta si no existe
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        results = []  # Colecciona resultados para la salida

        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            # Generar un nombre de archivo único, comenzando desde 1
            full_path = self.generate_unique_filename(save_path, filename_prefix, padding_length, filename_delimiter, starting_number=1)

            img.save(full_path, pnginfo=metadata, compress_level=4)

            # Almacena resultados para la salida
            results.append({
                "filename": os.path.basename(full_path),  # Solo el nombre del archivo
                "subfolder": save_path,
                "type": self.type
            })

        # Retorna las rutas de las imágenes guardadas como salida
        return {"ui": {"images": results}}

# Un diccionario que contiene todos los nodos que deseas exportar con sus nombres
NODE_CLASS_MAPPINGS = {
    "SaveImageNode": SaveImageNode
}

# Un diccionario que contiene los títulos amigables/humanos para los nodos
NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageNode": "Save Image Node"
}
