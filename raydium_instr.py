import json
class RayInstruction:
    pool_addr: str
    swap_in: int
    swap_out: int
    direction: bool

def parse_instruction(instr_data: json):
    # pool_index
    return  instr_data['accounts'][1]