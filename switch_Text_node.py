class AnyType_fill(str):
    def __ne__(self, __value: object) -> bool:
        return False

# Our any instance wants to be a wildcard string
anyType = AnyType_fill("*")

class SwitchNode:
    def __init__(self):
        self.Started = 0
        self.switch = 0
        self.mode = 0

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": ("INT", {"default": 0, "min": 0, "max": 9, "step": 1}),  # Integer to decide the output
                "source": (anyType, {}),  # Single input source
            }
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    RETURN_TYPES = (anyType,) * 10  # Up to 10 possible outputs
    RETURN_NAMES = tuple(f"SOURCE_{i}" for i in range(10))

    FUNCTION = "node"
    CATEGORY = "Custom Nodes"

    def node(self, condition, source):
        # Ensure the condition is within the allowed range (0-9)
        if 0 <= condition < 10:
            # Create a list of 10 outputs, setting the one matching 'condition' to 'source' and the others to 'None'
            outputs = [None] * 10
            outputs[condition] = source
            return tuple(outputs)
        else:
            raise ValueError(f"Error: The condition {condition} is out of the allowed range (0-9).")
