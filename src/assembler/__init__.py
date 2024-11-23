from .translator import *

__all__ = [f"encode_{inst}" for inst in (set(OPCODES.keys()) | set(FUNCTS.keys()))]
