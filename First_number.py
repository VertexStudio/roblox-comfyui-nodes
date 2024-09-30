class FirstDigitNode:
    # Define el tipo de entrada y salida
    input_types = {
        "required": {
            "number": ("INT", {}),  # Entrada: un número entero
        }
    }
    output_types = {
        "required": {
            "first_digit": ("INT", {}),  # Salida: el primer dígito como entero
        }
    }

    # Define los tipos de retorno y nombres de retorno como atributos de clase
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("first_digit",)

    def __init__(self):
        self.Started = 0

    @classmethod
    def INPUT_TYPES(cls):
        return cls.input_types

    @classmethod
    def OUTPUT_TYPES(cls):
        return cls.output_types

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    def node(self, number):
        if isinstance(number, int) and number > 0:
            # Obtener el primer dígito del número entero
            first_digit = int(str(number)[0])
            return (first_digit,)  # Devuelve el primer dígito como una tupla
        else:
            raise ValueError("La entrada debe ser un número entero positivo.")

    FUNCTION = "node"
    CATEGORY = "Custom Nodes"
