from .overlay_image_node import ScaleImageNode
from .switch_Image_node import SwitchImageNode
from .switch_Text_node import SwitchNode
from .First_number import FirstDigitNode
from .mirror_image_node import MirrorEffectNode
from .text_to_image_node import TextToImageNode
from .FlowNodes import FlowNodes
from .SaveImageNode import SaveImageNode


NODE_CLASS_MAPPINGS = {
    "ScaleImageNode": ScaleImageNode,
    "SwitchImageNode": SwitchImageNode,
    "SwitchTextNode": SwitchNode,
    "FirstLetterNode": FirstDigitNode,
    "MirrorEffectNode": MirrorEffectNode,
    "TextToImageNode": TextToImageNode,
    "FlowNodes" : FlowNodes,
    "SaveImageNode": SaveImageNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ScaleImageNode": "Scale Image Node",
    "SwitchImageNode": "Switch Image Node",
    "SwitchTextNode": "Switch Text Node",
    "FirstLetterNode": "First Number Node" ,
    "MirrorEffectNode": "Mirror Effect Node",
    "TextToImageNode": "Text To ImageNode",
    "FlowNodes":"Flow Nodes",
    "SaveImageNode":"Simple Save Image Node"
}
