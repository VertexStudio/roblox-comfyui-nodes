import nodes
import comfy
from server import PromptServer

# Clase que permite un comportamiento personalizado para tipos de datos
class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any_typ = AnyType("*")

current_prompt = None

def workflow_to_map(workflow):
    nodes = {}
    links = {}
    for link in workflow['links']:
        links[link[0]] = link[1:]
    for node in workflow['nodes']:
        nodes[str(node['id'])] = node

    return nodes, links

def collect_non_reroute_nodes(node_map, links, res, node_id):
    if node_map[node_id]['type'] != 'Reroute' and node_map[node_id]['type'] != 'Reroute (rgthree)':
        res.append(node_id)
    else:
        for link in node_map[node_id]['outputs'][0]['links']:
            next_node_id = str(links[link][2])
            collect_non_reroute_nodes(node_map, links, res, next_node_id)

def is_execution_model_version_supported():
    try:
        import comfy_execution
        return True
    except ImportError:
        return False

class FlowNodes:
    def __init__(self):
        self.cable_held = False  # Estado del cable

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": (any_typ,),
                "mode": ("INT", {"default": 1, "min": 0, "max": 1, "label_active": "1 - Active", "label_inactive": "0 - Inactive"}),
                "behavior": ("STRING", {"default": "Stop", "choices": ["Stop", "Mute", "Bypass"]}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            }
        }

    FUNCTION = "execute"

    CATEGORY = "FlowControl/Logic"
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("value",)
    OUTPUT_NODE = True

    DESCRIPTION = ("When behavior is 'Stop' and mode is active (1), the input value is passed to the output.\n"
                   "When behavior is 'Mute' or 'Bypass' and mode is active (1), connected nodes are altered accordingly.\n"
                   "When mode is inactive (0), the execution is halted.")

    @classmethod
    def IS_CHANGED(cls, value, mode, behavior="Stop", unique_id=None, prompt=None, extra_pnginfo=None):
        if mode == 0:
            return value, mode, behavior
        elif behavior == "Stop":
            return value, mode, behavior
        else:
            try:
                workflow = current_prompt['extra_data']['extra_pnginfo']['workflow']
            except KeyError:
                print("[FlowNodes] Error: Missing workflow data.")
                return 0

            nodes, links = workflow_to_map(workflow)
            next_nodes = []

            for link in nodes[unique_id]['outputs'][0]['links']:
                node_id = str(links[link][2])
                collect_non_reroute_nodes(nodes, links, next_nodes, node_id)

        return next_nodes

    def on_cable_drag(self):
        self.cable_held = True  # El cable está siendo sostenido

    def on_cable_release(self):
        self.cable_held = False  # El cable se ha soltado
        # Aquí puedes activar las salidas del nodo
        self.activate_outputs()

    def is_cable_released(self):
        return not self.cable_held  # Retorna True si el cable ha sido soltado

    def activate_outputs(self):
        # Aquí va la lógica para activar las salidas del nodo
        print("Activando salidas del nodo...")
        # Por ejemplo, podrías enviar un mensaje a PromptServer aquí

    def execute(self, value, mode, behavior="Stop", unique_id=None, prompt=None, extra_pnginfo=None):
        global error_skip_flag

        if is_execution_model_version_supported():
            from comfy_execution.graph import ExecutionBlocker
        else:
            print("[FlowNodes] ComfyUI version is outdated. 'Stop' behavior may not work correctly.")

        if mode == 0:
            return (ExecutionBlocker(None),)

        elif behavior == "Stop":
            return (value,)

        else:
            workflow_nodes, links = workflow_to_map(extra_pnginfo['workflow'])

            active_nodes = []
            mute_nodes = []
            bypass_nodes = []

            for link in workflow_nodes[unique_id]['outputs'][0]['links']:
                node_id = str(links[link][2])

                next_nodes = []
                collect_non_reroute_nodes(workflow_nodes, links, next_nodes, node_id)

                for next_node_id in next_nodes:
                    node_mode = workflow_nodes[next_node_id]['mode']

                    if node_mode == 0:
                        active_nodes.append(next_node_id)
                    elif node_mode == 2:
                        mute_nodes.append(next_node_id)
                    elif node_mode == 4:
                        bypass_nodes.append(next_node_id)

            if mode == 1:
                if behavior == "Mute":
                    should_be_mute_nodes = active_nodes + bypass_nodes
                    if should_be_mute_nodes:
                        PromptServer.instance.send_sync("flow-control-continue", {"node_id": unique_id, 'mutes': list(should_be_mute_nodes)})
                        nodes.interrupt_processing()

                elif behavior == "Bypass":
                    should_be_bypass_nodes = active_nodes + mute_nodes
                    if should_be_bypass_nodes:
                        PromptServer.instance.send_sync("flow-control-continue", {"node_id": unique_id, 'bypasses': list(should_be_bypass_nodes)})
                        nodes.interrupt_processing()

            return (value,)
