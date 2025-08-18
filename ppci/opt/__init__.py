from .clean import CleanPass
from .constantfolding import ConstantFolder
from .cse import CommonSubexpressionEliminationPass
from .load_after_store import LoadAfterStorePass
from .mem2reg import Mem2RegPromotor
from .transform import (
    BlockPass,
    DeleteUnusedInstructionsPass,
    FunctionPass,
    InstructionPass,
    ModulePass,
    RemoveAddZeroPass,
)

__all__ = [
    "ModulePass",
    "FunctionPass",
    "BlockPass",
    "InstructionPass",
    "CleanPass",
    "CommonSubexpressionEliminationPass",
    "ConstantFolder",
    "DeleteUnusedInstructionsPass",
    "LoadAfterStorePass",
    "Mem2RegPromotor",
    "RemoveAddZeroPass",
]
