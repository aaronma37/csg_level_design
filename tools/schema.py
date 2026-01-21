import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Tuple, Any

@dataclass
class LightEmitter:
    offset: Tuple[float, float, float]
    color: Tuple[float, float, float]
    intensity: float

@dataclass
class ParticleEmitter:
    offset: Tuple[float, float, float]
    system_id: str

@dataclass
class Instruction:
    op: str
    pos: Optional[Tuple[float, float, float]] = None
    size: Optional[Tuple[float, float, float]] = None
    color: Optional[Any] = None # int or list
    shape: Optional[str] = None
    points: Optional[List[Tuple[float, float, float]]] = None
    
    # Allow loose kwargs for other properties until fully mapped
    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class SnapPoint:
    pos: Tuple[float, float, float]

@dataclass
class Asset:
    name: str
    instructions: List[dict] = field(default_factory=list) # Keeping instructions loose for now as they come from VoxelBuilder
    light_emitters: List[LightEmitter] = field(default_factory=list)
    particle_emitters: List[ParticleEmitter] = field(default_factory=list)
    snap_points: dict[str, SnapPoint] = field(default_factory=dict)
    asset_tags: List[str] = field(default_factory=list)

    def add_light(self, offset: Tuple[float, float, float], color: Tuple[float, float, float], intensity: float):
        self.light_emitters.append(LightEmitter(offset, color, intensity))

    def add_particle(self, offset: Tuple[float, float, float], system_id: str):
        self.particle_emitters.append(ParticleEmitter(offset, system_id))

    def save(self, filepath: str):
        data = asdict(self)
        # Clean up None values in instructions if they were dataclasses, 
        # but currently instructions are often dicts from VoxelBuilder.
        # So we just dump.
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved asset '{self.name}' to {filepath}")
