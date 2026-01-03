import random
from primitives import volumes

def apply_pitting(instructions, pos, size, density=0.01, pit_radius=1):
    """
    PHYSICAL Meso-Detail: Randomly carves out small pits from a surface.
    Works well for stone or old wood.
    """
    x, y, z = pos
    w, d, h = size
    num_pits = int(w * d * h * density)
    
    for _ in range(num_pits):
        px = random.randint(x, x + w)
        py = random.randint(y, y + d)
        pz = random.randint(z, z + h)
        
        # We add a 'subtract' instruction with a small sphere
        instructions.append({
            "op": "subtract",
            "shape": "sphere",
            "pos": [px, py, pz],
            "radius": pit_radius
        })

def apply_material_noise(instructions, material_range=(21, 25), probability=0.1):
    """
    SHADER Micro-Detail: Shifts indices within a material family.
    This allows the shader's material properties to remain cohesive 
    while creating visual interest.
    """
    for op in instructions:
        if op.get('op') == 'add' and random.random() < probability:
            # Only jitter if the color is already within the target material family
            if material_range[0] <= op['color'] <= material_range[1]:
                op['color'] = random.randint(material_range[0], material_range[1])